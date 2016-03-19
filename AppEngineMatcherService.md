# This service is currently only available in the SDK as a trusted tester service. #
## Overview ##
The App Engine Matcher exposes Google’s highly scalable real-time matching infrastructure for use by App Engine apps. Matcher allows an app to register a set of queries to match against a stream of documents. For every document presented, matcher will return the ids of all the registered queries that match the document.

A document is an object with one or more named fields whose types are specified in a schema. Supported document types include db.Model, datastore.Entity and the native python dictionary (dict). Queries specify the condition under which they trigger as a logical expression on fields of the document.

As an example, a Person document is derived from db.Model and has three fields we can match on:
```
class Person(db.Model):
  name = db.StringProperty()
  birth = db.IntegerProperty()
  height_meters = db.FloatProperty()
```
We can register different queries on a Person document. For example:
```
matcher.subscribe(Person, “name: smith OR name:schmidt”, “smith”)
matcher.subscribe(Person, “birth < 1900”, “old”)
matcher.subscribe(Person, “height_meters > 2.0”, “tall”)
matcher.subscribe(Person, “birth > 1945 AND birth < 1965”, “boomer”)
```
Then a document can be constructed and presented using code like the following:
```
person = MatcherDocument()
person.name = “smith”
person.height_meters = 1.5
matcher.match(person)
```
Queries that match the presented document are returned to the application as one or more Task Queue Tasks. By default, these tasks are processed by the ‘/_ah/matcher’ HTTP POST handler._

## Document Schema ##
Matcher accepts documents which are derived from db.Model, datastore.Entity or the native python dictionary (dict) type. When presented to the match function, each document must be either implicitly or explicitly associated with a schema that maps field names to types.

Documents whose type is either datastore.Entity or python dictionary require a schema to be explicitly specified. However, for documents derived from db.Model, the schema is implicitly provided by the definition of the derived class.

A python dictionary document contains field names that map to the supported python types, for example:
```
person = {
 'name': 'Andrew Smith',
 'citizenship': 'Brazil',
 'birth': 1975,
 'height_meters': 1.54,
}
```
The schema maps underlying types to field names, for example:
```
PersonSchema = {
 str: ['name', 'citizenship'],
 int: ['birth']
 float: [height_meters']
}
```
## Query Language ##
**Text operators**
Text fields can be matched for the occurrence of a word or phrase anywhere in the content of the field. Text queries are case insensitive (Foo will match foo). For example:
```
field_text_a:horse
field_text_a:"horse riding"
```
**Numeric comparison operators**
The > >=, =, <= and < numeric operators are supported. For example:
```
height_meters > 1.5
```
**Logical operators**
Complex queries can be composed using the NOT, OR and AND operators. They can also be grouped using parentheses. For example:
```
field_int32_a > 20 AND field_int32_b = 10
(field_int32_a > 20 AND field_int32_b = 10) OR field_text_a:fox
```

## API methods ##
**subscribe**
The subscribe call is used to register subscriptions, which comprise of a subscription id and a query. A delay of a few seconds is expected between when subscribe returns successfully and when the subscription becomes registered and active. A successful subscribe call guarantees that the subscription will eventually be registered.
```
matcher.subscribe(document_class,
                 query,
                 sub_id,
                 schema=None,
                 topic=None,
                 lease_duration_sec=DEFAULT_LEASE_DURATION_SEC)
```
  * document\_class is either dict for python dictionary, datastore.Entity or a db.Model derived class name.
  * query is query string.
  * sub\_id is a unique string identifier for the subscription; subscribe will overwrite subscriptions with the same sub\_id.
  * schema must be specified if you are using a python dictionary or a datastore.Entity.
  * topic specifies the namespace for the subscription. Subscriptions of a particular topic will only be matched against documents of the same topic. Topic must be specified if you are using a python dictionary or a datastore.Entity, and it is by default set to the class name of document\_class if document\_class is derived from db.Model.
  * lease\_duration\_sec is the subscription lifetime. Subscriptions will be removed after this lease time has expired. The default and maximum lease duration is 24 hours. Typically, applications will need to resubscribe subscriptions that should be kept alive. See list\_subscriptions call.

**unsubscribe**
Subscriptions are removed from the system using the unsubscribe call. A successful unsubscribe call guarantees that the subscription will eventually be removed. A delay of a few seconds is expected between the unsubscribe returning successfully and the subscription being removed.
```
matcher.unsubscribe(document_class,
                   sub_id,
                   topic=None)
```
  * document\_class is either dict for python dictionary, datastore.Entity or a db.Model derived class name.
  * sub\_id is the id of the subscription to remove.
  * topic must be the same as of the subscription to be removed. Topic must be specified if you are using a python dictionary or a datastore.Entity, and it is by default set to document\_class if document\_class is derived from db.Model.

**match**
The match call is used to present a document for matching against all registered subscriptions of the same topic. The set of subscriptions matched are enqueued in batches as tasks on the TaskQueue.
```
matcher.match(document,
             topic=None,
             result_key=None,
             result_relative_url='/_ah/matcher',
             result_task_queue='default',
             result_batch_size=DEFAULT_RESULT_BATCH_SIZE,
             result_return_document=True)
```
  * document is the document to match, either python dictionary, datastore.Entity or a db.Model.
  * topic specifies the namespace for the subscriptions to match. Subscriptions of a particular topic will only be matched against documents of the same topic. Topic must be specified if you are using a python dictionary or a datastore.Entity, and it is by default set to the class name of the document if the document is derived from db.Model.
  * result\_key is a user defined key returned with the results that can be used to associate the result batch with a particular document.
  * result\_relative\_url is the relative url on which to generate the http POST event that delivers the result batch.
  * result\_task\_queue is the name of the TaskQueue to deliver the results on.
  * result\_batch\_size specifies the maximum number of subscription ids to put inside one result batch.
  * result\_return\_document determines if the document should be included with the result batch.

**list\_subscriptions**
The list\_subscriptions call is used to retrieve subscriptions that were previously created.
```
list_subscriptions(document_class,
                  sub_id_start="",
                  topic=None,
                  max_results=1000,
                  expires_before=None)
```
  * document\_class is a python dictionary, datastore.Entity or db.model class
  * sub\_id\_start specifies that no subscriptions which are lexicographically lower than the given value should be returned
  * topic must be specified if the document\_class is of type python dictionary or datastore.Entity. The topic specified should be the same as that used in the subscribe call
  * max\_results sets the maximum number of subscriptions that should be returned
  * expires\_before limits the returned subscriptions to those that expire before the specified epoch\_time.
This call returns a list of one or more tuples. Each tuple contains:
  * sub\_id is the subscription id
  * query is the query associated with the subscription
  * expiration\_time is the time, in seconds since the epoch, when the subscription will expire
  * state is one of:
    * OK -- Subscription is active
    * PENDING -- Successfully registered but not yet active
    * ERROR -- Inactive due to an error (see error value for explanation)
  * error is error text if the subscription state is ERROR
Example:
```
for sub in sub_list:
     (sub_id, query, expiration_time, state, error) = sub
              if matcher.SubscriptionState.ERROR:
                <do something useful>
```
**get\_documents**
The get\_document call is used to fetch a returned document from the task queue POST request.
```
matcher.get_document(request)
```
  * request is the TaskQueue generated POST request that contains the document

## Processing results ##
Match results are returned by the TaskQueue as http POST events to your application. You will need to point the result\_url path to your result handler, for example:
```
def main(argv):
 application = webapp.WSGIApplication(
     [('/', Main),
      ('/_ah/matcher', MatchResults)])
```
The result POST request is form data that is x-www-form-urlencoded. The POST request has the following parameters:
  * id is repeated for each matched subscription id in the current batch.
  * results\_count is the total number of subscription ids matched across all batches.
  * results\_offset is the offset of the current batch into the results\_count. (Example: If you set result\_batch\_size on the Match call to 2 and you have three matches, there will be two batches of results delivered. The first will have a results\_offsets equal to 0 and the second will have results\_offset = 2.)
  * key is the result\_key provided by the user in the Match call.
  * topic is the topic provided to the Match call or the db.Model class name
  * matcher.get\_document(self.request) reconstructs the document if result\_return\_document was set to True.

Here is an example of how to access the parameters:
```
class MatchResults(webapp.RequestHandler):
 def post(self):
   sub_ids = self.request.get_all('id')
   key = self.request.get('key')
   topic = self.request.get('topic')
   results_count = self.request.get('results_count')
   results_offset = self.request.get('results_offset')
   doc = matcher.get_document(self.request)
```
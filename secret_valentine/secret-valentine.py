#!/usr/bin/env python
#
# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Rafe Kaplan'

from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import cgi
import logging
import os
import sys

_DEBUG = True

# Change this value to an admin of your application
SECRET_VALENTINE_SENDER = 'secret.valentine.demo@gmail.com'


class SecretValentine(webapp.RequestHandler):
  """Index page handler.

  Generates form used to fill in information for secret valentine.
  """

  def get(self):
    """Get index page.

    The index page is generated by injecting a while bunch of HTML in to the
    index template.  This is a very simple form that does not attempt to
    remember any additional state about the application, such as previous
    selections.
    """
    # Resolve path to template.
    directory = os.path.dirname(__file__)
    path = os.path.join(directory, 'welcome.html')

    # Values used in template.  Each value for the form is an HTML input
    # form corresponding to the fields of the secret valentine.
    values = {
        'error_message': self.request.get('error_message'),

        # These HTML lines are in this file rather than a template because
        # the template for the sending email is the same as the template
        # for the input form.  See message_body.html.  Normally, it is
        # desirable to be more clever than this, but this is clear enough
        # for demonstration purposes.

        'salutation':
        '<select name="salutation">'
        '<option>Beloved</option>'
        '<option>My dearest</option>'
        '<option>Dear</option>'
        '<option>Hello</option>'
        '</select>',

        'receiver_name':
        '<input type="text" size="14" name="receiver_name">',

        'feeling_type':
        '<select name="feeling_type">'
        '<option>loving</option>'
        '<option>fond</option>'
        '<option>warm</option>'
        '<option>angry</option>'
        '<option>terrified</option>'
        '<option>loathing</option>'
        '</select>',

        'thinking_activity':
        '<select name="thinking_activity">'
        '<option>swoon</option>'
        '<option>lose my breath</option>'
        '<option>smile</option>'
        '<option>cry</option>'
        '<option>scream</option>'
        '<option>run</option>'
        '</select>',

        'will_be':
        '<select name="will_be">'
        '<option>admirer</option>'
        '<option>best friend</option>'
        '<option>friend</option>'
        '</select>',

        'good_bye':
        '<select name="good_bye">'
        '<option>, just yours</option>'
        '<option>lovingly</option>'
        '<option>truly</option>'
        '<option>sincerely</option>'
        '</select>',

        'secret_name': '&lt;your secret name&gt;'
    }

    self.response.out.write(template.render(path, values, _DEBUG))

class PostMail(webapp.RequestHandler):
  """Handles posting mail to recipient.

  Main form handler.  Merely receives fields and passes them to the
  EmailMessage class.
  """

  def handle_error(self, message):
    """Handle user error in input form.

    Places the error message in to the request and redirects the
    user back to the index page.

    Args:
      message: Message to display to the user upon error.
    """
    self.redirect('/compose?error_message=%s' % message)

  def get(self):
    """PostMail handler get method.

    The email is generated in potentially two forms, text and HTML.
    Each form of the mail has its own template each of which takes
    the same parameters.  The main function of this method is to
    pass the form parameters to one or both of the templates and
    pass the generated text to the email API.
    """

    directory = os.path.dirname(__file__)

    # Copy a subset of the form to the mail templates parameter
    # dict.
    values = dict((k, cgi.escape(self.request.get(k))) for k in (
        'salutation',
        'receiver_name',
        'feeling_type',
        'thinking_activity',
        'will_be',
        'good_bye',
        'secret_name'))

    if not values['secret_name'].strip():
      self.handle_error('What is your secret name?')
      return

    if not values['receiver_name'].strip():
      self.handle_error('Who are you sending this too?')
      return

    #############################
    #
    #  MAIN MAIL SENDING SECTION.
    #
    #############################

    # Generate an EmailMessage object without a body.
    try:
      message = mail.EmailMessage(sender=SECRET_VALENTINE_SENDER,
                                  to=self.request.get('email'),
                                  subject='A Secret Valentine!')

      # Report who really sent the email.
      user = users.get_current_user()
      values['nickname'] = user.nickname()
      values['user_email'] = user.email()
      message.reply_to = user.email()

      # Generate the body depending on format selection.
      # For each option, the templating engine is called to render
      # the mail body.
      format = self.request.get('format')
      if format == 'text' or format == 'both':
        template_file = os.path.join(directory, 'message.txt')
        message.body = template.render(template_file, values, _DEBUG)

      if format == 'html' or format == 'both':
        template_file = os.path.join(directory, 'message.html')
        message.html = template.render(template_file, values, _DEBUG)

      message.check_initialized()

    except mail.InvalidEmailError:
      self.handle_error('Invalid email recipient.')
      return
    except mail.MissingRecipientsError:
      self.handle_error('You must provide a recipient.')
      return
    except mail.MissingBodyError:
      self.handle_error('You must provide a mail format.')
      return

    # That's all there is to it!
    message.send()
    values['mime_message'] = cgi.escape(str(message.ToMIMEMessage()))

    # Render the sent page.
    path = os.path.join(directory, 'sent.html')
    self.response.out.write(template.render(path, values, _DEBUG))

_URLS = (
    ('/', SecretValentine),
    ('/compose', SecretValentine),
    ('/send', PostMail))


def main(argv):
  application = webapp.WSGIApplication(_URLS)
  run_wsgi_app(application)


if __name__ == '__main__':
  main(sys.argv)

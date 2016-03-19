# Introduction #

This project contains sample code that can be run on Google App Engine.  Each sample is checked in its own directory in the project's trunk. The samples highlight parts of the Google App Engine APIs, including samples that integrate Google App Engine with other web tools and APIs.

# Details #

Samples:

**trunk/geodatastore**: The GeoDataStore application allows you to store you geo data on the App Engine infrastructure. It comes with a backend server which can be accessed directly using Get and Post, as well as a Google Maps API front-end.

**trunk/myhangouts**: My Hangouts is a simple ajax applications that provides a simple RPC framework for making mostly abstract Python function calls from JavaScript. Provides a few simple functions for the My Hangouts application.This application uses the lower level Datastore API to make datastore calls and perform queries.

**trunk/secret\_valentine**: Secret Valentine is a demo of the mail api. Users fill out a form to send an email to a friend. The application replaces the form content with some secret content and sends an email to the specified user.

**trunk/tasks**: The Tasks application is a stylized task list. Its a collaborative task application that enables users to share task lists with one another and provides a simple access control mechanism.

**trunk/muvmuv**: MuvMuv is a simple movie review site that grabs the upcoming movies and find its movie trailer.

**trunk/blitz**: Blitz is an Ajax chess program with real time chat and persistent storage of game history.

**trunk/shell**: An interactive, stateful AJAX shell that runs Python code on the server. Deployed at [shell.appspot.com](http://shell.appspot.com/).

**trunk/openid-provider**: An [OpenID](http://openid.net/) provider. Allows Google users to log into OpenID consumer sites using their Google Account. Deployed at [openid-provider.appspot.com](http://openid-provider.appspot.com/).

**trunk/indexed-cached-zipserve**: Allows serving static files from zip files. Uses memcache to increase performance. It performs best when files zipped in alphabetical order so the handler can easily determine which zip file a given url is in.

**trunk/guestbook\_namespaces**: Namespace aware sample guestbook application for python App Engine. (Needs 1.3.6 or higher App Engine SDK)

**trunk/gwtguestbook-namespaces**: Namespace aware sample guestbook application for GWT/Java App Engine. (Needs 1.3.6 or higher App Engine SDK)
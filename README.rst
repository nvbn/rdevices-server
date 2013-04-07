rdevic.es server
================

For more information visit `rdevic.es <http://rdevic.es>`_.

Installation
------------

Install requirements::

    pip install -r requirements.txt
    npm install coffee-script -g
    gem install sass

You can install CoffeeScript and Sass from other source, but you need:
 - CoffeeScript >= 1.6
 - Sass >= 3.2

Copy settings::

    cp rdevices/settings/{dist,local}.py

Fill local settings values in  rdevices/settings/local.py:
 - ``REDIS_CREDENTIALS`` - redis connection credentials
 - ``NOTIFICATIONS_BIND`` - url of push notifications daemon
 - ``FACEBOOK_APP_ID``, ``FACEBOOK_SECRET_KEY``, ``FACEBOOK_REQUEST_PERMISSIONS`` - facebook app information for authentication
 - ``GITHUB_CLIENT_ID``, ``GITHUB_CLIENT_SECRET``, ``GITHUB_REQUEST_PERMISSIONS`` - github app information for authentication
 - ``TWITTER_CONSUMER_KEY``, ``TWITTER_CONSUMER_SECRET_KEY`` - twitter app information for authentication
 - ``GOOGLE_CLIENT_ID``, ``GOOGLE_CLIENT_SECRET`` - google app information for authentication

Running for developing
----------------------

Start http server with::

    ./manage.py runsever

Start server for communication with devices::

    ./manage.py run_connector

Start push notifications server::

    ./manage.py run_push


Testing
-------

For running tests run::

    ./manage.py test devices interface connector push_notifications

For faster testing use in-memory sqlite with::

    ./manage.py test devices interface connector push_notifications --settings=rdevices.test_settings

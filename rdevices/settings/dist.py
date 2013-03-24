DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

REDIS_CREDENTIALS = {
    'host': '',
    'port': 0,
    'db': 0,
}

USER_STORAGE_PREFIX = 'prefix'

EMAIL_BACKEND = ''

FACEBOOK_APP_ID = ''
FACEBOOK_SECRET_KEY = ''
FACEBOOK_REQUEST_PERMISSIONS = ''

GITHUB_CLIENT_ID = ''
GITHUB_CLIENT_SECRET = ''
GITHUB_REQUEST_PERMISSIONS = ''

TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET_KEY = ''

GOOGLE_CLIENT_ID = ''
GOOGLE_CLIENT_SECRET = ''

from settings import *


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CALLS_CHANNEL = 'calls_test'
NOTIFICATIONS_CHANNEL = 'notifications_test'

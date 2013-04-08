from settings import *
import sys


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

CALLS_CHANNEL = 'calls_test'
NOTIFICATIONS_CHANNEL = 'notifications_test'
TEST_CONNECTOR = 'localhost:9999'
TEST_PUSH = 'localhost:9990'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'connector': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'push_notifications': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

TEST_DAEMON_DB = 'test_daemons.db'

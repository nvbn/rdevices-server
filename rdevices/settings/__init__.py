from base import *
try:
    from local import *
except ImportError as e:
    print 'Copy dist.py to local.py and fill it'
    raise ImportError(e)

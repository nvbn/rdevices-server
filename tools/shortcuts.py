from django.conf import settings
from tools import connections
import json


def prettify(obj):
    """Prettify object"""
    return json.dumps(obj, ensure_ascii=False, indent=4)


def send_call_request(**request):
    """Send request to device"""
    connections.r.publish(
        settings.CALLS_CHANNEL, json.dumps(request),
    )

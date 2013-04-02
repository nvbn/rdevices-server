from django.conf import settings


def push(request):
    """Context processor for notifications bind"""
    return {
        'NOTIFICATIONS_BIND': settings.NOTIFICATIONS_BIND,
    }

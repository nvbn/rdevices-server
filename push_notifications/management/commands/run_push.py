from django.core.management.base import BaseCommand
from django.conf import settings
from tornado.ioloop import IOLoop
from push_notifications.server import NotificationServer


class Command(BaseCommand):
    help = 'Run push notifications daemon'
    args = ('address',)

    def handle(self, address='localhost:8080', *args, **options):
        """Run connector daemon"""
        if ':' in address:
            host, port = address.split(':')
        else:
            host = None
            port = address
        ioloop = IOLoop.instance()
        server = NotificationServer(settings.NOTIFICATIONS_CHANNEL)
        server.listen(port, host)
        ioloop.start()

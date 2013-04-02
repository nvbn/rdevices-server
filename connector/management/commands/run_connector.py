from django.core.management.base import BaseCommand
from django.conf import settings
from tornado.ioloop import IOLoop
from connector.server import DeviceServer


class Command(BaseCommand):
    help = 'Run connector daemon'
    args = ('address',)

    def handle(self, address='localhost:8080', *args, **options):
        """Run connector daemon"""
        if ':' in address:
            host, port = address.split(':')
        else:
            host = None
            port = address
        ioloop = IOLoop.instance()
        server = DeviceServer(
            settings.CALLS_CHANNEL,
            settings.NOTIFICATIONS_CHANNEL,
        )
        server.listen(port, host)
        ioloop.start()

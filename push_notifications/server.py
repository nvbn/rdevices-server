from sockjs.tornado import SockJSConnection, SockJSRouter
import tornadoredis
import tornado.gen
import tornado.web
import json
import logging


logger = logging.getLogger('push_notifications')


class PushConnection(SockJSConnection):
    """Push notifications connection"""
    users = {}

    def __init__(self, *args, **kwargs):
        super(PushConnection, self).__init__(*args, **kwargs)
        self.user_id = None

    def on_message(self, message):
        """Message received"""
        parsed = json.loads(message)
        if parsed['action'] == 'subscribe':
            self.subscribe(parsed['user_id'])

    def subscribe(self, user_id):
        """Subscribe user to notifications"""
        if self.user_id:
            self.unsubscribe()
        if not PushConnection.users.get(user_id):
            PushConnection.users[user_id] = []
        PushConnection.users[user_id].append(self)
        self.user_id = user_id

    def unsubscribe(self):
        """Unsubscrive user from notifiactions"""
        subscribers = PushConnection.users.get(self.user_id, [])
        subscribers.remove(self)

    def on_close(self):
        """Unsubscribe user on connection close"""
        if self.user_id:
            self.unsubscribe()

    def notify(self, message):
        """Notify user"""
        self.send(message)


class NotificationServer(tornado.web.Application):
    """Notifications server"""

    def __init__(self, notifications_channel):
        router = SockJSRouter(PushConnection, '/push')
        super(NotificationServer, self).__init__(router.urls)
        self._channel = notifications_channel
        self._init_channel()

    @tornado.gen.engine
    def _init_channel(self):
        """Init channel and start consumption"""
        self._r = tornadoredis.Client()
        self._r.connect()
        yield tornado.gen.Task(
            self._r.subscribe, self._channel,
        )
        self._r.listen(self._on_call)
        logger.info('Start consuming')

    def _on_call(self, msg):
        """On new call"""
        if not type(msg.body) in (str, unicode):
            # skip service messages
            return
        try:
            data = json.loads(msg.body)
            user_id = data['user_id']
            logger.info('Call:%s', msg.body)
            if PushConnection.users.get(user_id, None):
                for connection in PushConnection.users[user_id]:
                    connection.notify(data)
        except Exception as e:
            # fail silently
            logger.warning(e)

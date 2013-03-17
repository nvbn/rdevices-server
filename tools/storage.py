from django.conf import settings
import redis


class RedisStorage(object):
    """Redis storage"""

    @property
    def pool(self):
        """Laze redis pool"""
        if not hasattr(self, '_pool'):
            self._pool = redis.ConnectionPool(
                **getattr(settings.REDIS_CREDENTIALS)
            )
        return self._pool

    @property
    def connection(self):
        """Lazy redis connection"""
        if not hasattr(self, '_connection'):
            self._connection = redis.Redis(connection_pool=self.pool)
        return self._connection

    def get(self, key, default):
        """Get value from redis"""
        value = self.connection.get(key)
        if not value:
            value = default
        return value

    def set(self, key, value):
        """Set value to redis"""
        self.connection.set(key, value)


storage = RedisStorage()

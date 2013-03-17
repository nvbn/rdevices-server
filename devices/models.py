from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tools.storage import storage


class Device(models.Model):
    """Device"""
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    user = models.ForeignKey(User, verbose_name=_('user'))
    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')

    def __unicode__(self):
        return self.name

    def _prepare_key(self, key):
        """Convert device-level key to storage key"""
        return "{user_id}_{device_id}_{key}".format(
            user_id=self.user.id,
            device_id=self.id,
            key=key,
        )

    def set_value(self, key, value):
        """Store per device value"""
        storage.set(
            self._prepare_key(key), value,
        )

    def get_value(self, key, default=None):
        """Get per device value"""
        return storage.get(
            self._prepare_key(key), default,
        )


class DeviceAction(models.Model):
    """Device action"""
    KIND_EVENT = 0
    KIND_METHOD = 1
    KINDS = (
        (KIND_EVENT, _('event')),
        (KIND_METHOD, _('method')),
    )

    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    kind = models.PositiveSmallIntegerField(
        choices=KINDS,verbose_name=_('kind'),
    )
    device = models.ForeignKey(
        Device, verbose_name=_('device'),
    )
    name = models.CharField(
        max_length=300, verbose_name=_('name'),
    )
    spec = models.TextField(verbose_name=_('spec'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('device event')
        verbose_name_plural = _('device events')

    def __unicode__(self):
        return self.name

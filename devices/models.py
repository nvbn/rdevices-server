from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tools.storage import storage


class Device(models.Model):
    """Device"""
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    owner = models.ForeignKey(User, verbose_name=_('owner'))
    allowed_users = models.ManyToManyField(
        User, verbose_name=_('allowed users'),
        related_name='allowed_devices',
    )
    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')

    def __unicode__(self):
        return self.name

    def _prepare_key(self, key):
        """Convert device-level key to storage key"""
        return "{owner_id}_{device_id}_{key}".format(
            owner_id=self.owner.id,
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


class DeviceMethod(models.Model):
    """Device method"""
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    device = models.ForeignKey(
        Device, verbose_name=_('device'),
        related_name='methods',
    )
    name = models.CharField(
        max_length=300, verbose_name=_('name'),
    )
    spec = models.TextField(verbose_name=_('spec'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('device method')
        verbose_name_plural = _('device method')

    def __unicode__(self):
        return self.name


class DeviceMethodCall(models.Model):
    """Call of device method"""
    STATE_CREATED = 0
    STATE_FINISHED = 1
    STATE_ERROR = 2
    STATES = (
        (STATE_CREATED, _('created')),
        (STATE_FINISHED, _('finished')),
        (STATE_ERROR, _('error')),
    )

    caller = models.ForeignKey(User, verbose_name=_('caller'))
    state = models.PositiveSmallIntegerField(
        choices=STATES, default=STATE_CREATED,
    )
    method = models.ForeignKey(DeviceMethod, verbose_name=_('method'))
    request = models.TextField(verbose_name=_('request'))
    response = models.TextField(verbose_name=_('response'))

    class Meta:
        verbose_name = _('device method call')
        verbose_name_plural = _('devices methods calls')

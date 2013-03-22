from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from django_extensions.db.fields import AutoSlugField
from pprint import pformat
from jsonfield import JSONField
from tools.storage import storage


class Device(models.Model):
    """Device"""
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    slug = AutoSlugField(populate_from='name', verbose_name=_('slug'))
    owner = models.ForeignKey(User, verbose_name=_('owner'))
    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('description'),
    )
    image = models.ImageField(
        upload_to='device/%m/%d/', verbose_name=_('image'),
        blank=True, null=True,
    )

    class Meta:
        verbose_name = _('device')
        verbose_name_plural = _('devices')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'devices_item', [], {'slug': self.slug}

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
    """
        Device method

        spec = {
            'args': {
                'arg1: 'int',
                'arg2': 'str',
            },
            'result': 'int',
        }
    """
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    slug = AutoSlugField(populate_from='name', verbose_name=_('slug'))
    device = models.ForeignKey(
        Device, verbose_name=_('device'),
        related_name='methods',
    )
    name = models.CharField(
        max_length=300, verbose_name=_('name'),
    )
    spec = JSONField(blank=True, verbose_name=_('spec'))
    description = models.TextField(verbose_name=_('description'))

    class Meta:
        verbose_name = _('device method')
        verbose_name_plural = _('device method')

    def __unicode__(self):
        return self.name

    def get_spec_args(self):
        """Get spec arguments"""
        return self.spec.get('args', {})


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
    method = models.ForeignKey(
        DeviceMethod, verbose_name=_('method'),
        related_name='calls',
    )
    request = JSONField(verbose_name=_('request'))
    response = JSONField(verbose_name=_('response'))

    class Meta:
        verbose_name = _('device method call')
        verbose_name_plural = _('devices methods calls')

    def get_state(self):
        """Get textual state"""
        return dict(DeviceMethodCall.STATES)[self.state]

    def pretty_spec(self):
        """Get pretty spec"""
        return pformat(self.spec)

    def pretty_request(self):
        """Get pretty request"""
        return pformat(self.request)

    def pretty_response(self):
        """Get pretty response"""
        return pformat(self.response)

from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
from django.core.cache import cache
from django_extensions.db.fields import AutoSlugField, CreationDateTimeField
from jsonfield import JSONField
from pytils.translit import slugify
from datetime import datetime
from tools.shortcuts import prettify, send_call_request
from tools.fields import ReUUIDField
import json


def image_file_name(instance, filename):
    """Slugify device image filename"""
    now = datetime.now()
    return "device/{month}/{day}/{owner}_{filename}".format(
        month=now.month,
        day=now.day,
        owner=instance.owner.id,
        filename=slugify(filename),
    )


class Device(models.Model):
    """Device"""
    uuid = ReUUIDField(db_index=True, verbose_name=_('uuid'))
    slug = AutoSlugField(
        db_index=True, populate_from='name', verbose_name=_('slug'),
    )
    owner = models.ForeignKey(User, verbose_name=_('owner'))
    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('description'),
    )
    image = models.ImageField(
        upload_to=image_file_name,
        verbose_name=_('image'), blank=True, null=True,
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
    slug = AutoSlugField(
        db_index=True, populate_from='name', verbose_name=_('slug'),
    )
    device = models.ForeignKey(
        Device, verbose_name=_('device'),
        related_name='methods',
    )
    name = models.CharField(
        db_index=True, max_length=300, verbose_name=_('name'),
    )
    spec = JSONField(blank=True, verbose_name=_('spec'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('description'),
    )

    class Meta:
        verbose_name = _('device method')
        verbose_name_plural = _('device method')
        ordering = ('name',)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'devices_item', [], {
            'slug': self.device.slug,
            'method_slug': self.slug,
        }

    def get_spec_args(self):
        """Get spec arguments"""
        return self.spec.get('args', {})

    def pretty_spec(self):
        """Get pretty spec"""
        return prettify(self.spec)

    def get_json_args_example(self):
        """Get json args example"""
        args = self.spec.get('args', {})
        return json.dumps(
            {key: '{}Value'.format(key) for key in args},
        ).replace('"', '\\"')


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

    created = CreationDateTimeField(verbose_name=_('created'))
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
        ordering = ('-created',)

    def get_state(self):
        """Get textual state"""
        return dict(DeviceMethodCall.STATES)[self.state]

    def _get_request_cache_key(self):
        """Get request cache key"""
        return 'pretty_request_{id}'.format(id=self.id)

    def _get_response_cache_key(self):
        """Get response cache key"""
        return 'pretty_response_{id}'.format(id=self.id)

    def pretty_request(self):
        """Get pretty request"""
        key = self._get_request_cache_key()
        value = cache.get(key)
        if not value:
            value = prettify(self.request)
            cache.set(key, value)
        return value

    def pretty_response(self):
        """Get pretty response"""
        key = self._get_response_cache_key()
        value = cache.get(key)
        if not value:
            value = prettify(self.response)
            cache.set(key, value)
        return value

    def save(self, *args, **kwargs):
        """Save and clear caches"""
        super(DeviceMethodCall, self).save(*args, **kwargs)
        self._clear_caches()

    def _clear_caches(self):
        """Clear caches"""
        cache.delete_many([
            self._get_request_cache_key(),
            self._get_response_cache_key(),
        ])

    def send_request(self):
        """Send call request"""
        send_call_request(
            action='request',
            method=self.method.name,
            request_id=self.id,
            uuid=self.method.device.uuid,
            request=self.request,
        )


@receiver(post_save, sender=DeviceMethodCall)
def send_request(sender, instance, created, **kwargs):
    """Send to call request to device"""
    if created:
        instance.send_request()


class Dashboard(models.Model):
    """Dashboard for device or user"""
    owner = models.ForeignKey(User, verbose_name=_('owner'))
    slug = AutoSlugField(populate_from='name', verbose_name=_('slug'))
    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(
        blank=True, null=True, verbose_name=_('description'),
    )
    image = models.ImageField(
        upload_to=image_file_name,
        verbose_name=_('image'), blank=True, null=True,
    )
    code = models.TextField(blank=True, null=True, verbose_name=_('code'))
    preview = models.TextField(
        blank=True, null=True, verbose_name=_('preview'),
    )

    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        kwargs = {
            'slug': self.slug,
        }
        return 'devices_dashboard', [], kwargs

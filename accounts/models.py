from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile
from uuid import uuid4
from hashlib import sha1
import hmac


class Profile(UserenaBaseProfile):
    """User profile"""
    user = models.OneToOneField(
        User, unique=True, verbose_name=_('user'),
        related_name='profile',
    )

    def is_social(self):
        """Check is social"""
        return self.user.facebookprofile_set.count() \
            or self.user.githubprofile_set.count() \
            or self.user.twitterprofile_set.count() \
            or self.user.googleprofile_set.count()


class ApiKey(models.Model):
    """ApiKey with ForeignKey to user"""
    user = models.ForeignKey(User, related_name='api_keys')
    key = models.CharField(
        max_length=256, blank=True, default='', db_index=True,
        verbose_name=_('key'),
    )
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )

    def __unicode__(self):
        return u"%s for %s" % (self.key, self.user)

    def save(self, *args, **kwargs):
        """Save and generate api key"""
        if not self.key:
            self.key = self.generate_key()

        return super(ApiKey, self).save(*args, **kwargs)

    def generate_key(self):
        """Generate random api key"""
        new_uuid = uuid4()
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()


from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext as _
from userena.models import UserenaBaseProfile


class Profile(UserenaBaseProfile):
    """User profile"""
    user = models.OneToOneField(
        User, unique=True, verbose_name=_('user'),
        related_name='profile',
    )
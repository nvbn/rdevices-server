from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
import os


class ModelCase(TestCase):
    """Test for model"""

    def setUp(self):
        """Create initial data"""
        self.client = Client()
        self.user = User.objects.create(
            username='user',
            is_active=True,
        )
        self.user.set_password('user')
        self.user.save()

    def test_redirect(self):
        """Test redirect if authenticated"""
        self.client.login(
            username='user',
            password='user',
        )
        response = self.client.get(reverse('site_index'))
        self.assertIsInstance(response, HttpResponseRedirect)

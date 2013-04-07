from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.files import File
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from interface.models import CarouselEntry
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

    def test_enabled(self):
        """Test enabled in manager"""
        entry = CarouselEntry.objects.create(
            url='http://rdevic.es',
            title='title',
            text='text',
            is_enabled=False,
        )
        self.assertEqual(CarouselEntry.objects.enabled().count(), 0)
        entry.is_enabled = True
        entry.save()
        self.assertItemsEqual(CarouselEntry.objects.enabled(), [entry])

    def test_redirect(self):
        """Test redirect if authenticated"""
        self.client.login(
            username='user',
            password='user',
        )
        response = self.client.get(reverse('site_index'))
        self.assertIsInstance(response, HttpResponseRedirect)

    def test_index(self):
        """Test index page"""
        test_file = open(os.path.join(
            settings.MEDIA_ROOT,
            'test.png',
        ))
        entry = CarouselEntry.objects.create(
            url='http://rdevic.es',
            title='title',
            text='text',
            image=File(test_file),
        )
        response = self.client.get(reverse('site_index'))
        self.assertItemsEqual(
            response.context['carousel'], [entry],
        )

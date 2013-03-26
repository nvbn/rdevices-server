from django.test import TestCase
from django.contrib.auth.models import User
from devices.models import Device


class DeviceTest(TestCase):
    """Device tests"""

    def setUp(self):
        """Create initial data"""
        self.root = User.objects.create(
            username='root',
            is_superuser=True,
        )
        self.device = Device.objects.create(
            is_enabled=True,
            owner=self.root,
            name='test',
            description='test',
        )

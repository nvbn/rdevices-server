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
            user=self.root,
            name='test',
            description='test',
        )

    def test_storage(self):
        """Test device storage"""
        self.device.set_value('test', '123')
        self.assertEqual(
            self.device.get_value('test'), '123',
        )
        self.assertEqual(
            self.device.get_value('test2', '567'), '567',
        )

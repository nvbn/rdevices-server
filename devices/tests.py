from django.test import TestCase
from django.contrib.auth.models import User
from devices.models import Device, DeviceMethodCall, DeviceMethod
from devices.forms import (
    CreateDeviceForm, UpdateDeviceForm, DeviceMethodCallForm,
    CreateDashboardForm, UpdateDashboardForm,
)


class ModelTestCase(TestCase):
    """Test model"""

    def setUp(self):
        """Create initial data"""
        self.root = User.objects.create(
            username='root',
            is_superuser=True,
        )
        self.device = Device.objects.create(
            owner=self.root,
            name='test',
            description='test',
        )

    def test_pretty_method_caches(self):
        """Test pretty methods caches"""
        method = DeviceMethod.objects.create(
            device=self.device,
            spec={},
            name='test',
        )
        call = DeviceMethodCall.objects.create(
            method=method,
            caller=self.root,
            request='123',
            response='456',
        )

        self.assertGreater(
            len(call.pretty_request()), 1,
        )
        self.assertGreater(
            len(call.pretty_response()), 1,
        )

        prev_request = call.pretty_request()
        prev_response = call.pretty_response()

        call.request = {
            'a': 1,
        }
        call.response = {
            'b': 2,
        }
        call.save()

        self.assertNotEqual(
            prev_request, call.pretty_request(),
        )
        self.assertNotEqual(
            prev_response, call.pretty_response(),
        )


class FormsTestCase(TestCase):
    """Test forms"""

    def setUp(self):
        """Create initial data"""
        self.root = User.objects.create(
            username='root',
            is_superuser=True,
        )
        self.device = Device.objects.create(
            owner=self.root,
            name='test',
            description='test',
        )

    def test_create_device(self):
        """Test device creating"""
        description = '567'
        form = CreateDeviceForm(self.root, {
            'name': '123',
            'description': description,
        })
        self.assertTrue(form.is_valid())
        device = form.save()
        self.assertEqual(device.description ,description)

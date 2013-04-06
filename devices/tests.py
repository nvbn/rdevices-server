from django.test import TestCase
from django.contrib.auth.models import User
from devices.models import (
    Device, DeviceMethodCall, DeviceMethod, Dashboard,
)
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
            request='request',
            response='response',
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
            name='test name',
            description='test description',
        )

    def test_create_device(self):
        """Test device creating"""
        description = 'test description in create'
        form = CreateDeviceForm(self.root, {
            'name': 'test name in create',
            'description': description,
        })
        self.assertTrue(form.is_valid())
        device = form.save()
        self.assertEqual(device.description, description)

    def test_update_device(self):
        """Test update device"""
        description = 'test description in update'
        user = User.objects.create(username='test_user')
        form = UpdateDeviceForm({
            'owner': user,
            'name': 'test name in update',
            'description': description,
        }, instance=self.device)
        self.assertTrue(form.is_valid())
        device = form.save()
        self.assertEqual(device.owner, self.root)
        self.assertEqual(device.description, description)

    def test_device_method_call(self):
        """Test device method call form"""
        method = DeviceMethod.objects.create(
            name='test_method',
            device=self.device,
            spec={
                'args': {
                    'x': 'str',
                    'y': 'str',
                },
                'result': 'int',
            },
        )
        CallForm = DeviceMethodCallForm.create_form(method, self.root)

        form = CallForm({})
        self.assertFalse(form.is_valid())

        form = CallForm({
            'x': '14',
            'y': '15',
        })
        self.assertTrue(form.is_valid())
        call = form.save()
        self.assertEqual(call.request['x'], '14')
        self.assertEqual(call.request['y'], '15')

    def test_create_dashboard(self):
        """Test create dashboard form"""
        dashboard_name = 'dashboard name in create'
        form = CreateDashboardForm(self.root, {
            'name': dashboard_name,
            'description': 'dashboard description in create',
        })
        self.assertTrue(form.is_valid())
        dashboard = form.save()
        self.assertEqual(dashboard.name, dashboard_name)

    def test_update_dashboard(self):
        """Test update dashboard"""
        dashboard = Dashboard.objects.create(
            name='dashboard name',
            description='dashboard description',
            owner=self.root,
        )
        user = User.objects.create(username='test_user')
        dashboard_name = 'updated dashboard name'
        form = UpdateDashboardForm({
            'name': dashboard_name,
            'description': 'dashboard description',
            'owner': user,
        }, instance=dashboard)
        self.assertTrue(form.is_valid())
        dashboard = form.save()
        self.assertEqual(dashboard.owner, self.root)
        self.assertEqual(dashboard.name, dashboard_name)

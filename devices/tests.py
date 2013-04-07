from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.views.generic.base import ContextMixin
from django.test.client import Client
from django.core.urlresolvers import reverse
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


class ViewsTestCase(TestCase):
    """Test case for views"""

    def setUp(self):
        """Create initial data"""
        self.root = User.objects.create(
            username='root',
            is_superuser=True,
            is_active=True,
        )
        self.user1 = User.objects.create(
            username='user1',
            is_active=True,
        )
        self.user1.set_password('user1')
        self.user1.save()
        self.user2 = User.objects.create(
            username='user2',
            is_active=True,
        )
        self.client = Client()
        self.client.login(
            username='user1',
            password='user1',
        )
        self.user1_device = Device.objects.create(
            name='device 1',
            description='description',
            owner=self.user1,
        )
        self.user2_device = Device.objects.create(
            name='device 2',
            description='description',
            owner=self.user2,
        )

    def _patch_view_class(self):
        """Patch view class for storing last context"""
        self.last_context = None
        case = self

        def get_context_data(self, **kwargs):
            if 'view' not in kwargs:
                kwargs['view'] = self
            case.last_context = kwargs
            return kwargs
        ContextMixin.get_context_data = get_context_data

    def test_device_list(self):
        """Test device list"""
        devices = map(
            lambda name: Device.objects.create(
                name=str(name),
                owner=self.user1,
                description=str(name),
            ),
            range(10),
        ) + [self.user1_device]
        response = self.client.get(reverse('devices_list'))
        self.assertItemsEqual(
            response.context['devices'], devices,
        )

    def test_device_list_access(self):
        """Test device list access"""
        map(
            lambda name: Device.objects.create(
                name=str(name),
                owner=self.user2,
                description=str(name),
            ),
            range(10),
        )
        response = self.client.get(reverse('devices_list'))
        self.assertItemsEqual(
            response.context['devices'], [self.user1_device],
        )

    def test_device_item(self):
        """Test device item"""
        response = self.client.get(reverse(
            'devices_item', kwargs={'slug': self.user1_device.slug},
        ))
        self.assertEqual(
            response.context['device'], self.user1_device,
        )

    def test_device_item_access(self):
        """Test device item access"""
        response = self.client.get(reverse(
            'devices_item', kwargs={'slug':  self.user2_device.slug},
        ))
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_device_create(self):
        """Test device create"""
        name = 'test device name'
        self.client.post(reverse('devices_create'), {
            'name': name,
            'description': 'description',
        })
        device = Device.objects.get(name=name)
        self.assertEqual(device.name, name)
        self.assertEqual(device.owner, self.user1)

    def test_device_change(self):
        """Test device change"""
        changed_name = 'changed name'
        self.client.post(
            reverse(
                'devices_change', kwargs={'slug': self.user1_device.slug},
            ), {
                'name': changed_name,
                'description': 'description',
            },
        )
        device = Device.objects.get(id=self.user1_device.id)
        self.assertEqual(device.name, changed_name)

    def test_device_change_access(self):
        """Test device change access"""
        name = 'changed name'
        response = self.client.post(
            reverse(
                'devices_change', kwargs={'slug':  self.user2_device.slug},
            ), {
                'name': name,
                'description': 'description',
            },
        )
        self.assertIsInstance(response, HttpResponseNotFound)
        device = Device.objects.get(id= self.user2_device.id)
        self.assertNotEqual(device.name, name)

    def test_device_delete(self):
        """Test device delete"""
        self.client.post(reverse('devices_delete', kwargs={
            'slug': self.user1_device.slug,
        }))
        with self.assertRaises(Device.DoesNotExist):
            Device.objects.get(id=self.user1_device.id)

    def test_device_delete_access(self):
        """Test device delete"""
        response = self.client.post(reverse('devices_delete', kwargs={
            'slug': self.user2_device.slug,
        }))
        self.assertIsInstance(response, HttpResponseNotFound)
        self.assertEqual(
            self.user2_device, Device.objects.get(id= self.user2_device.id),
        )

    def test_device_regenerate_uuid(self):
        """Test device regenerate uuid"""
        device_uuid = self.user1_device.uuid
        self.client.post(reverse('devices_regenerate', kwargs={
            'slug': self.user1_device.slug,
        }))
        device = Device.objects.get(id=self.user1_device.id)
        self.assertNotEqual(device.uuid, device_uuid)

    def test_device_regenerate_uuid_access(self):
        """Test device regenerate uuid access"""
        device_uuid =  self.user2_device.uuid
        response = self.client.post(reverse('devices_regenerate', kwargs={
            'slug':  self.user2_device.slug,
        }))
        self.assertIsInstance(response, HttpResponseNotFound)
        device = Device.objects.get(id= self.user2_device.id)
        self.assertEqual(device.uuid, device_uuid)

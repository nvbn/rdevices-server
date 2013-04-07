from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
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
        self._create_users()
        self._create_client()
        self._create_devices()
        self._create_methods()
        self._create_dashboards()

    def _create_users(self):
        """Create test users"""
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

    def _create_client(self):
        """Create test client"""
        self.client = Client()
        self.client.login(
            username='user1',
            password='user1',
        )

    def _create_devices(self):
        """Create test devices"""
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

    def _create_methods(self):
        """Create test methods"""
        self.user1_method = DeviceMethod.objects.create(
            device=self.user1_device,
            name='method 1',
            spec={
                'args': {
                    'x': 'str',
                    'y': 'str',
                },
                'result': 'str',
            }
        )
        self.user2_method = DeviceMethod.objects.create(
            device=self.user2_device,
            name='method 2',
            spec={
                'args': {
                    'x': 'str',
                    'y': 'str',
                },
                'result': 'str',
            }
        )

    def _create_dashboards(self):
        """Create test dashboards"""
        self.user1_dashboard = Dashboard.objects.create(
            owner=self.user1,
            name='dashboard 1',
            description='description 1',
        )
        self.user2_dashboard = Dashboard.objects.create(
            owner=self.user2,
            name='dashboard 2',
            description='description 2',
        )

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
        self.assertItemsEqual(
            response.context['dashboards'], [self.user1_dashboard],
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
        device = Device.objects.get(id=self.user2_device.id)
        self.assertEqual(device.uuid, device_uuid)

    def test_device_method_call_create_get(self):
        """Test GET to device method call create"""
        response = self.client.get(reverse('devices_call', kwargs={
            'device_slug': self.user1_device.slug,
            'device_method_slug': self.user1_method.slug,
        }))
        self.assertEqual(
            response.context['device'], self.user1_device,
        )
        self.assertEqual(
            response.context['device_method'], self.user1_method,
        )

    def test_device_method_call_create_get_access(self):
        """Test GET to device method call create access"""
        response = self.client.get(reverse('devices_call', kwargs={
            'device_slug': self.user2_device.slug,
            'device_method_slug': self.user2_method.slug,
        }))
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_device_method_call_create_post(self):
        """Test POST to device method call create"""
        self.client.post(
            reverse('devices_call', kwargs={
                'device_slug': self.user1_device.slug,
                'device_method_slug': self.user1_method.slug,
            }),
            {
                'x': '1',
                'y': '2',
            },
        )
        call = DeviceMethodCall.objects.filter(
            method=self.user1_method,
        ).order_by('-id')[0]
        self.assertEqual(call.caller, self.user1)
        self.assertEqual(call.request['x'], '1')

    def test_device_method_call_create_post_access(self):
        """Test POST to device method call create access"""
        response = self.client.post(
            reverse('devices_call', kwargs={
                'device_slug': self.user1_device.slug,
                'device_method_slug': self.user2_method.slug,
            }),
            {
                'x': '1',
                'y': '2',
            },
        )
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_dashboard_create(self):
        """Test create dashboard"""
        name = 'dashboard'
        self.client.post(reverse('devices_dashboard_create'), {
            'name': name,
            'description': 'description',
        })
        dashboard = Dashboard.objects.order_by('-id')[0]
        self.assertEqual(dashboard.name, name)
        self.assertEqual(dashboard.owner, self.user1)

    def test_dashboard_change(self):
        """Test changing dashboard"""
        name = 'changed name'
        self.client.post(
            reverse('devices_dashboard_change', kwargs={
                'slug': self.user1_dashboard.slug,
            }),
            {
                'name': name,
            }
        )
        dashboard = Dashboard.objects.get(id=self.user1_dashboard.id)
        self.assertEqual(dashboard.name, name)

    def test_dashboard_change_access(self):
        """Test changing dashboard"""
        name = 'changed name'
        response = self.client.post(
            reverse('devices_dashboard_change', kwargs={
                'slug': self.user2_dashboard.slug,
            }),
            {
                'name': name,
            }
        )
        self.assertIsInstance(response, HttpResponseNotFound)
        dashboard = Dashboard.objects.get(id=self.user2_dashboard.id)
        self.assertNotEqual(dashboard.name, name)

    def test_dashboard_item(self):
        """Test dashboard item"""
        response = self.client.get(reverse('devices_dashboard', kwargs={
            'slug': self.user1_dashboard.slug,
        }))
        self.assertEqual(response.context['dashboard'], self.user1_dashboard)

    def test_dashboard_item_access(self):
        """Test dashboard item access"""
        response = self.client.get(reverse('devices_dashboard', kwargs={
            'slug': self.user2_dashboard.slug,
        }))
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_dashboard_code(self):
        """Test dashboard code"""
        response = self.client.get(reverse('devices_dashboard_code', kwargs={
            'slug': self.user1_dashboard.slug,
        }))
        self.assertEqual(response.context['dashboard'], self.user1_dashboard)
        self.assertItemsEqual(
            response.context['devices'], [self.user1_device],
        )

    def test_dashboard_code_access(self):
        """Test dashboard code access"""
        response = self.client.get(reverse('devices_dashboard_code', kwargs={
            'slug': self.user2_dashboard.slug,
        }))
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_dashboard_delete(self):
        """Test dashboard delete"""
        self.client.post(reverse('devices_dashboard_delete', kwargs={
            'slug': self.user1_dashboard.slug,
        }))
        with self.assertRaises(Dashboard.DoesNotExist):
            Dashboard.objects.get(id=self.user1_dashboard.id)

    def test_dashboard_delete_access(self):
        """Test dashboard code access"""
        response = self.client.post(
            reverse('devices_dashboard_delete', kwargs={
                'slug': self.user2_dashboard.slug,
            }),
        )
        self.assertIsInstance(response, HttpResponseNotFound)
        self.assertEqual(
            self.user1_dashboard,
            Dashboard.objects.get(id=self.user1_dashboard.id),
        )

    def test_preview(self):
        """Test preview"""
        response = self.client.get(reverse('devices_preview', kwargs={
            'slug': self.user1_dashboard.slug,
        }))
        self.assertEqual(
            response.context['dashboard'],
            self.user1_dashboard,
        )

    def test_preview_access(self):
        """Test preview access"""
        response = self.client.get(reverse('devices_preview', kwargs={
            'slug': self.user2_dashboard.slug,
        }))
        self.assertIsInstance(response, HttpResponseNotFound)

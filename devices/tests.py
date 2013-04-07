from django.test import TestCase
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound
from django.test.client import Client
from django.core.urlresolvers import reverse
from tastypie.test import ResourceTestCase
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
        self.method = DeviceMethod.objects.create(
            device=self.device,
            spec={},
            name='test',
        )
        self.call = DeviceMethodCall.objects.create(
            method=self.method,
            caller=self.root,
            request='request',
            response='response',
        )

    def test_pretty_request_caches(self):
        """Test pretty request caches"""
        self.assertGreater(
            len(self.call.pretty_request()), 1,
        )
        prev_request = self.call.pretty_request()
        self.call.request = {
            'a': 1,
        }
        self.call.save()
        self.assertNotEqual(
            prev_request, self.call.pretty_request(),
        )

    def test_pretty_response_caches(self):
        """Test pretty response caches"""
        self.assertGreater(
            len(self.call.pretty_response()), 1,
        )
        prev_response = self.call.pretty_response()
        self.call.response = {
            'b': 2,
        }
        self.call.save()
        self.assertNotEqual(
            prev_response, self.call.pretty_response(),
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


class BasicDataMixin(object):
    """Mixin with basic data without fixtures"""

    def setUp(self):
        """Create initial data"""
        self._create_users()
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


class ViewsTestCase(TestCase, BasicDataMixin):
    """Test case for views"""

    def setUp(self):
        """Create initial data"""
        BasicDataMixin.setUp(self)
        self._create_client()

    def _create_client(self):
        """Create test client"""
        self.client = Client()
        self.client.login(
            username='user1',
            password='user1',
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


class ResourcesTestCase(ResourceTestCase, BasicDataMixin):
    """Test case for resources"""

    def setUp(self):
        """Create initial data"""
        super(ResourcesTestCase, self).setUp()
        BasicDataMixin.setUp(self)
        self._authenticate()

    def _authenticate(self):
        """Authenticate client"""
        self.api_client.client.login(
            username='user1',
            password='user1',
        )

    def test_device_create(self):
        """Test create device"""
        response = self.api_client.post(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'device',
                'api_name': 'v1',
            }),
            data={
                'name': 'created device',
                'description': 'device description',
            },
            format='json',
        )
        self.assertHttpMethodNotAllowed(response)

    def test_device_read(self):
        """Test read device"""
        response = self.api_client.get(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device',
                'api_name': 'v1',
                'pk': self.user1_device.pk,
            }),
            format='json',
        )
        self.assertEqual(
            self.deserialize(response)['name'],
            self.user1_device.name,
        )

    def test_device_read_access(self):
        """Test read device access"""
        response = self.api_client.get(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device',
                'api_name': 'v1',
                'pk': self.user2_device.pk,
            }),
            format='json',
        )
        self.assertHttpUnauthorized(response)

    def test_device_update(self):
        """Test update device"""
        response = self.api_client.put(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device',
                'api_name': 'v1',
                'pk': self.user1_device.pk,
            }),
            data={
                'name': 'created device',
                'description': 'device description',
            },
            format='json',
        )
        self.assertHttpMethodNotAllowed(response)

    def test_device_delete(self):
        """Test delete device"""
        response = self.api_client.delete(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device',
                'api_name': 'v1',
                'pk': self.user1_device.pk,
            }),
            format='json',
        )
        self.assertHttpMethodNotAllowed(response)

    def test_device_list(self):
        """Test read device"""
        response = self.api_client.get(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'device',
                'api_name': 'v1',
            }),
            format='json',
        )
        self.assertItemsEqual(
            map(lambda device: device['name'], self.deserialize(response)['objects']),
            [self.user1_device.name],
        )

    def test_device_method_create(self):
        """Test create device method"""
        response = self.api_client.post(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'device_method',
                'api_name': 'v1',
            }),
            data={
                'name': 'created device',
                'description': 'method description',
            },
            format='json',
        )
        self.assertHttpMethodNotAllowed(response)

    def test_device_method_read(self):
        """Test read device method"""
        response = self.api_client.get(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method',
                'api_name': 'v1',
                'pk': self.user1_method.pk,
            }),
            format='json',
        )
        self.assertEqual(
            self.deserialize(response)['name'],
            self.user1_method.name,
        )

    def test_device_method_read_access(self):
        """Test read device method access"""
        response = self.api_client.get(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method',
                'api_name': 'v1',
                'pk': self.user2_method.pk,
            }),
            format='json',
        )
        self.assertHttpUnauthorized(response)

    def test_device_method_update(self):
        """Test update device method"""
        response = self.api_client.put(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method',
                'api_name': 'v1',
                'pk': self.user1_method.pk,
            }),
            data={
                'name': 'created device method',
                'description': 'device method description',
            },
            format='json',
        )
        self.assertHttpMethodNotAllowed(response)

    def test_device_method_delete(self):
        """Test delete device method"""
        response = self.api_client.delete(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method',
                'api_name': 'v1',
                'pk': self.user1_method.pk,
            }),
            format='json',
        )
        self.assertHttpMethodNotAllowed(response)

    def test_device_list(self):
        """Test read device"""
        response = self.api_client.get(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'device_method',
                'api_name': 'v1',
            }),
            format='json',
        )
        self.assertItemsEqual(
            map(lambda method: method['name'], self.deserialize(response)['objects']),
            [self.user1_method.name],
        )

    def test_device_method_call_create(self):
        """Test create device method"""
        method = reverse('api_dispatch_detail', kwargs={
            'resource_name': 'device_method',
            'api_name': 'v1',
            'pk': self.user1_method.pk,
        })
        response = self.api_client.post(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'device_method_call',
                'api_name': 'v1',
            }),
            data={
                'method': method,
                'request': {
                    'x': '1',
                    'y': '2,'
                },
            },
            format='json',
        )
        self.assertHttpCreated(response)
        call = DeviceMethodCall.objects.order_by('-id')[0]
        self.assertEqual(call.request['x'], '1')
        self.assertEqual(call.caller, self.user1)

    def test_device_method_call_create_access(self):
        """Test device method call create access"""
        method = reverse('api_dispatch_detail', kwargs={
            'resource_name': 'device_method',
            'api_name': 'v1',
            'pk': self.user2_method.pk,
        })
        response = self.api_client.post(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'device_method_call',
                'api_name': 'v1',
            }),
            data={
                'method': method,
                'request': {
                    'x': '1',
                    'y': '2,'
                },
            },
            format='json',
        )
        self.assertHttpUnauthorized(response)

    def test_device_method_call_update(self):
        """Test device method call update"""
        call = DeviceMethodCall.objects.create(
            request={},
            method=self.user1_method,
            caller=self.user1,
        )
        method = reverse('api_dispatch_detail', kwargs={
            'resource_name': 'device_method',
            'api_name': 'v1',
            'pk': self.user1_method.pk,
        })
        response = self.api_client.put(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method_call',
                'api_name': 'v1',
                'pk': call.pk,
            }),
            data={
                'method': method,
                'request': {
                    'x': '1',
                    'y': '2,'
                },
            },
            format='json',
        )
        self.assertHttpUnauthorized(response)

    def test_device_method_call_delete(self):
        """Test device method call delete"""
        call = DeviceMethodCall.objects.create(
            request={},
            method=self.user1_method,
            caller=self.user1,
        )
        method = reverse('api_dispatch_detail', kwargs={
            'resource_name': 'device_method',
            'api_name': 'v1',
            'pk': self.user1_method.pk,
        })
        response = self.api_client.delete(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method_call',
                'api_name': 'v1',
                'pk': call.pk,
            }),
            data={
                'method': method,
                'request': {
                    'x': '1',
                    'y': '2,'
                },
            },
            format='json',
        )
        self.assertHttpUnauthorized(response)

    def test_device_method_call_prettify(self):
        """Test device method call prettify"""
        call = DeviceMethodCall.objects.create(
            request={},
            method=self.user1_method,
            caller=self.user1,
        )
        response = self.api_client.get(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'device_method_call',
                'api_name': 'v1',
                'pk': call.pk,
            }) + '?with_pretty=true',
            format='json',
        )
        call = self.deserialize(response)
        self.assertGreater(
            len(call['pretty_request']), 1,
        )
        self.assertGreater(
            len(call['pretty_response']), 1,
        )

    def test_dashboard_create(self):
        """Test dashboard create"""
        name = 'dashboard name'
        response = self.api_client.post(
            reverse('api_dispatch_list', kwargs={
                'resource_name': 'dashboard',
                'api_name': 'v1',
            }),
            data={
                'name': name,
                'description': 'description',
                'code': 'code',
            },
            format='json',
        )
        self.assertHttpCreated(response)
        dashboard = Dashboard.objects.order_by('-id')[0]
        self.assertEqual(dashboard.name, name)
        self.assertEqual(dashboard.owner, self.user1)

    def test_dashboard_update(self):
        """Test dashboard update"""
        name = 'new dashboard name'
        self.api_client.put(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'dashboard',
                'api_name': 'v1',
                'pk': self.user1_dashboard.pk,
            }),
            data={
                'name': name,
                'description': 'description',
                'code': 'code',
            },
            format='json',
        )
        dashboard = Dashboard.objects.get(id=self.user1_dashboard.id)
        self.assertEqual(dashboard.name, name)
        self.assertEqual(dashboard.owner, self.user1)

    def test_dashboard_update_access(self):
        """Test dashboard update access"""
        name = 'new dashboard name'
        response = self.api_client.put(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'dashboard',
                'api_name': 'v1',
                'pk': self.user2_dashboard.pk,
            }),
            data={
                'name': name,
                'description': 'description',
                'code': 'code',
            },
            format='json',
        )
        self.assertHttpUnauthorized(response)
        dashboard = Dashboard.objects.get(id=self.user2_dashboard.id)
        self.assertNotEqual(dashboard.name, name)

    def test_dashboard_delete(self):
        """Test dashboard delete"""
        self.api_client.delete(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'dashboard',
                'api_name': 'v1',
                'pk': self.user1_dashboard.pk,
            }),
            format='json',
        )
        with self.assertRaises(Dashboard.DoesNotExist):
            Dashboard.objects.get(id=self.user1_dashboard.id)

    def test_dashboard_delete_access(self):
        """Test dashboard delete access"""
        response = self.api_client.delete(
            reverse('api_dispatch_detail', kwargs={
                'resource_name': 'dashboard',
                'api_name': 'v1',
                'pk': self.user2_dashboard.pk,
            }),
            format='json',
        )
        self.assertHttpUnauthorized(response)
        self.assertEqual(
            self.user2_dashboard,
            Dashboard.objects.get(id=self.user2_dashboard.id),
        )

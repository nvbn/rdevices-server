from devices.models import (
    Device, DeviceMethod, DeviceMethodCall, Dashboard,
)
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Unauthorized
from tastypie import fields


class DeviceAuthorization(DjangoAuthorization):
    """Authorization for device"""

    def read_list(self, object_list, bundle):
        """Return only owner devices"""
        return super(DeviceAuthorization, self).read_list(
            object_list.filter(owner=bundle.request.user), bundle,
        )

    def read_detail(self, object_list, bundle):
        """Return only owner device"""
        if bundle.obj.owner == bundle.request.user:
            return super(DeviceAuthorization, self).read_detail(
                object_list, bundle,
            )
        else:
            raise Unauthorized('Not your device')


class DeviceResource(ModelResource):
    """Resource for devices"""
    methods = fields.ToManyField(
        'devices.resources.DeviceMethodResource', 'methods',
        blank=True, full=False,
    )

    class Meta:
        queryset = Device.objects.all()
        resource_name = 'device'
        allowed_methods = ('get',)
        authorization = DeviceAuthorization()
        excludes = ('owner',)


class DeviceMethodAuthorization(DjangoAuthorization):
    """Authorization for device methods"""

    def read_list(self, object_list, bundle):
        """Return only owner devices"""
        return super(DeviceMethodAuthorization, self).read_list(
            object_list.filter(device__owner=bundle.request.user), bundle,
        )

    def read_detail(self, object_list, bundle):
        """Return only owner device"""
        if bundle.obj.device.owner == bundle.request.user:
            return super(DeviceMethodAuthorization, self).read_detail(
                object_list, bundle,
            )
        else:
            raise Unauthorized('Not your device')


class DeviceMethodResource(ModelResource):
    """Resource for device methods"""
    device = fields.ToOneField(DeviceResource, 'device')
    calls = fields.ToManyField(
        'devices.resources.DeviceMethodCallResource', 'calls',
        blank=True, full=False,
    )

    class Meta:
        queryset = DeviceMethod.objects.all()
        resource_name = 'device_method'
        authorization = DeviceMethodAuthorization()
        allowed_methods = ('get',)


class DeviceMethodCallResource(ModelResource):
    """Resource for device method calls"""
    method = fields.ToOneField(DeviceMethodResource, 'method')

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            caller=request.user,
        )

    def obj_create(self, bundle, **kwargs):
        """Create call with caller"""
        return super(DeviceMethodCallResource, self).obj_create(
            bundle, caller=bundle.request.user, **kwargs
        )

    def dehydrate(self, bundle):
        """Add pretty field to bundle"""
        bundle.data['text_state'] = bundle.obj.get_state()
        if bundle.request.GET.get('with_pretty'):
            bundle.data['pretty_request'] = bundle.obj.pretty_request()
            bundle.data['pretty_response'] = bundle.obj.pretty_response()
        return bundle

    class Meta:
        queryset = DeviceMethodCall.objects.all()
        resource_name = 'device_method_call'
        authorization = DjangoAuthorization()
        filtering = {
            'method': ['exact'],
        }
        always_return_data = True
        list_allowed_methods = ('get', 'post', 'put')
        detailed_allowed_methods = ('get',)
        excludes = ('caller',)


class DashboardResource(ModelResource):
    """Resource for dashboards"""

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            owner=request.user,
        )

    class Meta:
        queryset = Dashboard.objects.all()
        resource_name = 'dashboard'
        authorization = DjangoAuthorization()
        allowed_methods = ('get', 'post', 'put', 'delete', 'patch')
        excludes = ('slug', 'owner', 'image')

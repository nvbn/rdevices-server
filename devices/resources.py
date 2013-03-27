from devices.models import (
    Device, DeviceMethod, DeviceMethodCall, Dashboard,
)
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie import fields


class DeviceResource(ModelResource):
    """Resource for devices"""
    methods = fields.ToManyField(
        'devices.resources.DeviceMethodResource', 'methods',
        blank=True, full=False,
    )

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            owner=request.user,
        )

    class Meta:
        queryset = Device.objects.all()
        resource_name = 'device'
        authorization = DjangoAuthorization()


class DeviceMethodResource(ModelResource):
    """Resource for device methods"""
    device = fields.ToOneField(DeviceResource, 'device')
    calls = fields.ToManyField(
        'devices.resources.DeviceMethodCallResource', 'calls',
        blank=True, full=False,
    )

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            device__owner=request.user,
        )

    class Meta:
        queryset = DeviceMethod.objects.all()
        resource_name = 'device_method'
        authorization = DjangoAuthorization()


class DeviceMethodCallResource(ModelResource):
    """Resource for device method calls"""
    method = fields.ToOneField(DeviceMethodResource, 'method')

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            caller=request.user,
        )

    class Meta:
        queryset = DeviceMethodCall.objects.all()
        resource_name = 'device_method_call'
        authorization = DjangoAuthorization()
        filtering = {
            'method': ['exact'],
        }


class DashboardResource(ModelResource):
    """Resource for dashboards"""
    device = fields.ToOneField(
        DeviceResource, 'device', blank=True, full=False,
    )

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            owner=request.user,
        )

    class Meta:
        queryset = Dashboard.objects.all()
        resource_name = 'dashboard'
        authorization = DjangoAuthorization()

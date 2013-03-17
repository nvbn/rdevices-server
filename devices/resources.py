from devices.models import Device, DeviceMethod
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie import fields


class DeviceResource(ModelResource):
    """Resource for devices"""
    methods = fields.ToManyField(
        'devices.resources.DeviceMethodResource', 'methods',
    )

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            owner=request.user,
        )

    class Meta:
        queryset = Device.objects.all()
        resource_name = 'my/device'
        authorization = DjangoAuthorization()


class DeviceMethodResource(ModelResource):
    """Resource for device methods"""
    device = fields.ToOneField(DeviceResource, 'device')

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            device__owner=request.user,
        )

    class Meta:
        queryset = DeviceMethod.objects.all()

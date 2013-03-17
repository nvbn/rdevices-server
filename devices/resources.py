from devices.models import Device
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization


class DeviceResource(ModelResource):
    """Resource for devices"""

    def apply_authorization_limits(self, request, object_list):
        """Only user resources"""
        return object_list.filter(
            owner=request.user,
        )

    class Meta:
        queryset = Device.objects.all()
        resource_name = 'my/device'
        authorization = DjangoAuthorization()

from django.conf.urls import patterns, include, url
from tastypie.api import Api
from devices.resources import (
    DeviceResource, DeviceMethodResource,
    DeviceMethodCallResource, DashboardResource,
)


api_v1 = Api(api_name='v1')
api_v1.register(DeviceResource())
api_v1.register(DeviceMethodResource())
api_v1.register(DeviceMethodCallResource())
api_v1.register(DashboardResource())


urlpatterns = patterns(
    '',
    url(r'^', include(api_v1.urls)),
)

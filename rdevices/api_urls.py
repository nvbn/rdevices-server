from django.conf.urls import patterns, include, url
from tastypie.api import Api
from devices.resources import DeviceResource


api_v1 = Api(api_name='v1')
api_v1.register(DeviceResource())

urlpatterns = patterns(
    '',
    url(r'^', include(api_v1.urls)),
    url(r'^doc/', include(
        'tastypie_swagger.urls', namespace='tastypie_swagger',
    )),
)

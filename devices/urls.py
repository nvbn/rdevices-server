from django.conf.urls import patterns, url
from devices.views import DeviceList, DeviceCreate


urlpatterns = patterns(
    'interface.views',
    url(r'^list/$', DeviceList.as_view(), name='devices_list'),
    url(r'^create/$', DeviceCreate.as_view(), name='devices_create'),
)

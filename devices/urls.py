from django.conf.urls import patterns, url
from devices.views import (
    DeviceList, DeviceCreate, DeviceItem, DeviceChange,
    DeviceDelete,
)


urlpatterns = patterns(
    'interface.views',
    url(r'^list/$', DeviceList.as_view(), name='devices_list'),
    url(r'^create/$', DeviceCreate.as_view(), name='devices_create'),
    url(r'^(?P<slug>.*)/change/$', DeviceChange.as_view(), name='devices_change'),
    url(r'^(?P<slug>.*)/delete/$', DeviceDelete.as_view(), name='devices_delete'),
    url(r'^(?P<slug>.*)/$', DeviceItem.as_view(), name='devices_item'),
)

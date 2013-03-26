from django.conf.urls import patterns, url
from devices.views import (
    DeviceList, DeviceCreate, DeviceItem, DeviceChange,
    DeviceDelete, DeviceMethodCallCreate, DeviceRegenerateUUID,
    DashboardCreate, DashboardChange, DashboardItem,
)


urlpatterns = patterns(
    'interface.views',
    url(r'^list/$', DeviceList.as_view(), name='devices_list'),
    url(r'^create/$', DeviceCreate.as_view(), name='devices_create'),
    url(
        r'^(?P<device>.*)/dashboard/create/$',
        DashboardCreate.as_view(), name='devices_dashboard_create',
    ),
    url(
        r'^dashboard/create/$',
        DashboardCreate.as_view(), name='devices_dashboard_create',
    ),
    url(
        r'^(?P<device>.*)/dashboard/(?P<slug>.*)/change/$',
        DashboardChange.as_view(), name='devices_dashboard_change',
    ),
    url(
        r'dashboard/(?P<slug>.*)/change/$',
        DashboardChange.as_view(), name='devices_dashboard_change',
    ),
    url(
        r'^(?P<device>.*)/dashboard/(?P<slug>.*)/$',
        DashboardItem.as_view(), name='devices_dashboard',
    ),
    url(
        r'^dashboard/(?P<slug>.*)/$',
        DashboardItem.as_view(), name='devices_dashboard',
    ),
    url(r'^(?P<slug>.*)/change/$', DeviceChange.as_view(), name='devices_change'),
    url(r'^(?P<slug>.*)/delete/$', DeviceDelete.as_view(), name='devices_delete'),
    url(
        r'^(?P<slug>.*)/regenerate/$', DeviceRegenerateUUID.as_view(),
        name='devices_regenerate',
    ),
    url(
        r'^(?P<device_slug>.*)/(?P<device_method_slug>.*)/call/$',
        DeviceMethodCallCreate.as_view(), name='devices_call',
    ),
    url(
        r'^(?P<slug>.*)/(?P<method_slug>.*)/$',
        DeviceItem.as_view(), name='devices_item',
    ),
    url(r'^(?P<slug>.*)/$', DeviceItem.as_view(), name='devices_item'),
)

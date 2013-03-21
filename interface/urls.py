from django.conf.urls import patterns, url
from interface.views import Index, DeviceList


urlpatterns = patterns(
    'interface.views',
    url(r'^$', Index.as_view(), name='site_index'),
    url(r'^devices/$', DeviceList.as_view(), name='site_devices'),
)

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'interface.views',
    url(r'^$', 'index', name='site_index'),
    url(r'^devices/$', 'devices', name='site_devices'),
)

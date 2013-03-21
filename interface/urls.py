from django.conf.urls import patterns, url
from interface.views import Index


urlpatterns = patterns(
    'interface.views',
    url(r'^$', Index.as_view(), name='site_index'),
)

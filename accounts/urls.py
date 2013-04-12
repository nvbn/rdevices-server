from django.conf.urls import patterns, url
from accounts.views import ApiKeyList, ApiKeyCreate, ApiKeyDelete


urlpatterns = patterns(
    'accounts.views',
    url(
        r'^(?P<username>.*)/keys/$', ApiKeyList.as_view(),
        name='accounts_keys_list',
    ),
    url(
        r'^(?P<username>.*)/keys/create/$', ApiKeyCreate.as_view(),
        name='accounts_keys_create',
    ),
    url(
        r'^(?P<username>.*)/keys/(?P<slug>.*)/delete/$', ApiKeyDelete.as_view(),
        name='accounts_keys_delete',
    ),
)

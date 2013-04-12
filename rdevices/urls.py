from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import api_urls


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^', include('interface.urls')),
    url(r'^devices/', include('devices.urls')),
    url(r'^api/', include(api_urls)),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^accounts/', include('userena.urls')),
    url(r'^social/', include(
        'socialregistration.urls', namespace='socialregistration',
    )),
    url(r'^pages', include('django.contrib.flatpages.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += patterns(
        '',
        url(
            r'^media/(?P<path>.*)$',
            'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT
            },
        ),
    ) + staticfiles_urlpatterns()

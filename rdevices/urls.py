from django.conf.urls import patterns, include, url
from django.contrib import admin
import api_urls


admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^', include('interface.urls')),
    url(r'^api/', include(api_urls)),
    url(r'^accounts/', include('userena.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

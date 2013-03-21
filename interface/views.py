from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from devices.models import Device
from interface.models import CarouselEntry, NewsEntry
from django.views.generic import TemplateView, ListView
from tools.mixins import LoginRequiredMixin


class Index(TemplateView):
    """Index page"""
    template_name = 'site/index.html'

    def get(self, request, *args, **kwargs):
        """Redirect to devices if authorised"""
        if request.user.is_authenticated():
            return redirect(reverse('site_devices'))
        else:
            return super(Index, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get carousel and news"""
        return {
            'carousel': CarouselEntry.objects.enabled(),
            'news': NewsEntry.objects.enabled(),
        }


class DeviceList(LoginRequiredMixin, ListView):
    """Device list view"""
    template_name = 'site/devices.html'
    context_object_name = 'devices'

    def get_queryset(self):
        """Get devices queryset"""
        return Device.objects.filter(
            owner=self.request.user,
        )

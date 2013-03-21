from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from interface.models import CarouselEntry, NewsEntry
from django.views.generic import TemplateView, ListView


class Index(TemplateView):
    """Index page"""
    template_name = 'interface/index.html'

    def get(self, request, *args, **kwargs):
        """Redirect to devices if authorised"""
        if request.user.is_authenticated():
            return redirect(reverse('devices_list'))
        else:
            return super(Index, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get carousel and news"""
        return {
            'carousel': CarouselEntry.objects.enabled(),
            'news': NewsEntry.objects.enabled(),
        }

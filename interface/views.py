from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView


class Index(TemplateView):
    """Index page"""
    template_name = 'interface/index.html'

    def get(self, request, *args, **kwargs):
        """Redirect to devices if authorised"""
        if request.user.is_authenticated():
            return redirect(reverse('devices_list'))
        else:
            return super(Index, self).get(request, *args, **kwargs)

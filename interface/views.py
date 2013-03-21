from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from devices.models import Device


@render_to('site/index.html')
def index(request):
    """Index page"""
    if request.user.is_authenticated():
        return redirect(reverse('site_devices'))
    return {}


@login_required
@render_to('site/devices.html')
def devices(request):
    """Devices page"""
    return {
        'devices': Device.objects.filter(
            owner=request.user,
        ),
    }

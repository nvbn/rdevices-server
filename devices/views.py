from devices.models import Device
from django.views.generic import ListView, CreateView, UpdateView
from tools.mixins import LoginRequiredMixin
from devices.forms import DeviceForm


class DeviceList(LoginRequiredMixin, ListView):
    """Device list view"""
    template_name = 'devices/list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        """Get devices queryset"""
        return Device.objects.filter(
            owner=self.request.user,
        )


class DeviceCreate(LoginRequiredMixin, CreateView):
    """Create device view"""
    template_name = 'devices/create.html'
    model = Device
    form_class = DeviceForm

    def get_form_kwargs(self):
        """Add owner to kwargs"""
        kwargs = super(DeviceCreate, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs

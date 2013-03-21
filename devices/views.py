from devices.models import Device
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView,
)
from django.core.urlresolvers import reverse_lazy
from tools.mixins import LoginRequiredMixin
from devices.forms import CreateDeviceForm, UpdateDeviceForm


class DeviceMixin(object):
    """Mixin for devices"""
    model = Device

    def get_queryset(self):
        """Get devices queryset"""
        return Device.objects.filter(
            owner=self.request.user,
        )


class DeviceList(DeviceMixin, LoginRequiredMixin, ListView):
    """Device list view"""
    template_name = 'devices/list.html'
    context_object_name = 'devices'


class DeviceItem(DeviceMixin, LoginRequiredMixin, DetailView):
    """Device item view"""
    template_name = 'devices/item.html'
    context_object_name = 'device'


class DeviceCreate(DeviceMixin, LoginRequiredMixin, CreateView):
    """Create device view"""
    template_name = 'devices/create.html'
    form_class = CreateDeviceForm

    def get_form_kwargs(self):
        """Add owner to kwargs"""
        kwargs = super(DeviceCreate, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs


class DeviceChange(DeviceMixin, LoginRequiredMixin, UpdateView):
    """Change device view"""
    template_name = 'devices/change.html'
    form_class = UpdateDeviceForm
    context_object_name = 'device'


class DeviceDelete(DeviceMixin, LoginRequiredMixin, DeleteView):
    """Delete device view"""
    success_url = reverse_lazy('devices_list')
    template_name = 'devices/delete.html'
    context_object_name = 'device'

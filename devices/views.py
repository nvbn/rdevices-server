from django.shortcuts import get_object_or_404, redirect
from devices.models import (
    Device, DeviceMethod, DeviceMethodCall, Dashboard,
)
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView,
    TemplateView,
)
from django.core.urlresolvers import reverse_lazy
from tools.mixins import LoginRequiredMixin
from devices.forms import (
    CreateDeviceForm, UpdateDeviceForm, DeviceMethodCallForm,
    CreateDashboardForm, UpdateDashboardForm,
)


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

    def get_context_data(self, **kwargs):
        """Put dashboards to context"""
        context = super(DeviceList, self).get_context_data(**kwargs)
        context['dashboards'] = Dashboard.objects.filter(
            owner=self.request.user,
        )
        return context


class DeviceItem(DeviceMixin, LoginRequiredMixin, DetailView):
    """Device item view"""
    template_name = 'devices/item.html'
    context_object_name = 'device'

    def get_context_data(self, **kwargs):
        """Add call forms to context"""
        context = super(DeviceItem, self).get_context_data(**kwargs)
        context['methods'] = map(
            lambda method: {
                'method': method,
                'form': DeviceMethodCallForm.create_form(
                    method, self.request.user,
                ),
            }, context['device'].methods.all(),
        )
        if 'method_slug' in self.kwargs:
            context['active_method'] = get_object_or_404(
                DeviceMethod, slug=self.kwargs['method_slug'],
            )
        return context


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


class DeviceRegenerateUUID(DeviceMixin, LoginRequiredMixin, DetailView):
    """Regenerate device uuid"""
    template_name = 'devices/regenerate.html'
    context_object_name = 'device'

    def post(self, *args, **kwargs):
        return self.regenerate_uuid()

    def regenerate_uuid(self):
        self.object = self.get_object()
        self.object.uuid = None
        self.object.save()
        return redirect(self.object.get_absolute_url())


class DeviceMethodCallCreate(LoginRequiredMixin, CreateView):
    """Create device method call view"""
    template_name = 'devices/call.html'
    model = DeviceMethodCall

    @property
    def device(self):
        """Lazy device"""
        if not hasattr(self, '_device'):
            self._device = get_object_or_404(
                Device, slug=self.kwargs['device_slug'],
            )
        return self._device

    @property
    def device_method(self):
        """Lazy device method"""
        if not hasattr(self, '_device_method'):
            self._device_method = get_object_or_404(
                DeviceMethod,
                slug=self.kwargs['device_method_slug'],
                device=self.device,
            )
        return self._device_method

    def get_success_url(self):
        """Get success url"""
        return self.device_method.get_absolute_url() + '#active'

    def get_context_data(self, **kwargs):
        """Add device method to context"""
        context = super(DeviceMethodCallCreate, self).get_context_data(
            **kwargs
        )
        context['device_method'] = self.device_method
        context['device'] = self.device
        return context

    def get_form_class(self):
        """Get form class"""
        return DeviceMethodCallForm.create_form(
            self.device_method, self.request.user,
        )


class DashboardCreate(LoginRequiredMixin, CreateView):
    """Create dashboard view"""
    template_name = 'devices/dashboard_create.html'
    form_class = CreateDashboardForm
    model = Dashboard

    def get_form_kwargs(self):
        """Add owner to kwargs"""
        kwargs = super(DashboardCreate, self).get_form_kwargs()
        kwargs['owner'] = self.request.user
        return kwargs


class DashboardChange(LoginRequiredMixin, UpdateView):
    """Change dashboard view"""
    template_name = 'devices/dashboard_change.html'
    form_class = UpdateDashboardForm
    context_object_name = 'dashboard'
    model = Dashboard

    def get_queryset(self):
        """Get dashboard queryset"""
        return Dashboard.objects.filter(
            owner=self.request.user,
        )


class DashboardItem(LoginRequiredMixin, DetailView):
    """Dashboard view"""
    template_name = 'devices/dashboard.html'
    context_object_name = 'dashboard'
    model = Dashboard

    def get_queryset(self):
        """Get dashboard queryset"""
        return Dashboard.objects.filter(
            owner=self.request.user,
        )


class DashboardCode(DashboardItem):
    """Change dashboard code"""
    template_name = 'devices/dashboard_code.html'

    def get_context_data(self, **kwargs):
        """Pass all available devices to context"""
        context = super(DashboardCode, self).get_context_data(**kwargs)
        context['devices'] = Device.objects.filter(
            owner=self.request.user,
        )
        return context


class DashboardDelete(LoginRequiredMixin, DeleteView):
    """Delete device view"""
    template_name = 'devices/dashboard_delete.html'
    context_object_name = 'dashboard'
    model = Dashboard

    def get_queryset(self):
        """Get dashboard queryset"""
        return Dashboard.objects.filter(
            owner=self.request.user,
        )

    def get_success_url(self):
        return '/'


class PreviewTemplate(TemplateView):
    """Template for preview"""
    template_name = "devices/preview_template.html"

    def get_context_data(self, **kwargs):
        """Send dashboard to context"""
        return {
            'dashboard': get_object_or_404(
                Dashboard, slug=self.kwargs['slug'],
            ),
        }

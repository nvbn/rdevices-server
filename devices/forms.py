from django import forms
from devices.models import Device, DeviceMethodCall, Dashboard


class CreateDeviceForm(forms.ModelForm):
    """Create device form"""

    class Meta:
        model = Device
        fields = (
            'name', 'description', 'image',
        )

    def __init__(self, owner, *args, **kwargs):
        """Set owner"""
        super(CreateDeviceForm, self).__init__(*args, **kwargs)
        self._owner = owner

    def save(self, *args, **kwargs):
        """Set owner and save"""
        self.instance.owner = self._owner
        return super(CreateDeviceForm, self).save(*args, **kwargs)


class UpdateDeviceForm(forms.ModelForm):
    """Update device form"""

    class Meta:
        model = Device
        fields = (
            'name', 'description', 'image',
            'is_enabled',
        )
        widgets = {
            'image': forms.FileInput,
        }


class DeviceMethodCallForm(forms.ModelForm):
    """Device method call form"""

    class Meta:
        model = DeviceMethodCall
        fields = []

    def save(self, *args, **kwargs):
        """Set caller and request and save"""
        self.instance.caller = self._caller
        self.instance.method = self._method
        self._create_request()
        return super(DeviceMethodCallForm, self).save(*args, **kwargs)

    def _create_request(self):
        """Create request from data"""
        self.instance.request = {}
        for field in self._method.get_spec_args().keys():
            self.instance.request[field] = self.cleaned_data.get(field)

    @staticmethod
    def _fields_from_spec(method):
        """Create fields from spec"""
        fields = {}
        for field, field_type in method.get_spec_args().items():
            fields[field] = forms.CharField(
                label=field,
            )
        return fields

    @classmethod
    def create_form(cls, method, caller):
        """Create form for caller and method"""
        return type('NewForm', (cls,), dict(
            _caller=caller,
            _method=method,
            **DeviceMethodCallForm._fields_from_spec(method)
        ))


class CreateDashboardForm(forms.ModelForm):
    """Create dashboard form"""

    class Meta:
        model = Dashboard
        fields = (
            'name', 'description', 'image',
        )

    def __init__(self, owner, device, *args, **kwargs):
        """Set owner"""
        super(CreateDashboardForm, self).__init__(*args, **kwargs)
        self._owner = owner
        self._device = device

    def save(self, *args, **kwargs):
        """Set owner and save"""
        self.instance.owner = self._owner
        self.instance.device = self._device
        return super(CreateDashboardForm, self).save(*args, **kwargs)


class UpdateDashboardForm(forms.ModelForm):
    """Update dashboard form"""

    class Meta:
        model = Dashboard
        fields = (
            'name', 'description', 'image',
        )

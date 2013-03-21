from django import forms
from devices.models import Device


class CreateDeviceForm(forms.ModelForm):
    """Create device form"""

    def __init__(self, owner, *args, **kwargs):
        """Set owner"""
        super(CreateDeviceForm, self).__init__(*args, **kwargs)
        self._owner = owner

    def save(self, *args, **kwargs):
        """Set owner and save"""
        self.instance.owner = self._owner
        return super(CreateDeviceForm, self).save(*args, **kwargs)

    class Meta:
        model = Device
        fields = (
            'name', 'description', 'image',
        )


class UpdateDeviceForm(forms.ModelForm):
    """Update device form"""

    class Meta:
        model = Device
        fields = (
            'name', 'description', 'image',
            'is_enabled',
        )

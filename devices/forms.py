from django import forms
from devices.models import Device


class DeviceForm(forms.ModelForm):
    """Device form"""

    def __init__(self, owner, *args, **kwargs):
        """Set owner"""
        super(DeviceForm, self).__init__(*args, **kwargs)
        self._owner = owner

    def save(self, *args, **kwargs):
        """Set owner and save"""
        self.instance.owner = self._owner
        return super(DeviceForm, self).save(*args, **kwargs)

    class Meta:
        model = Device
        fields = (
            'name', 'description',
        )

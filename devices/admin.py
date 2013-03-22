from django.contrib import admin
from devices.models import Device, DeviceMethod, DeviceMethodCall


admin.site.register(Device)
admin.site.register(DeviceMethod)
admin.site.register(DeviceMethodCall)

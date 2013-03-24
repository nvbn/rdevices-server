from django.contrib import admin
from interface.models import CarouselEntry


class CarouselEntryAdmin(admin.ModelAdmin):
    """Admin for carousel entry"""
    list_display = ('id', 'is_enabled', 'title')
    list_editable = ('is_enabled',)


admin.site.register(CarouselEntry, CarouselEntryAdmin)

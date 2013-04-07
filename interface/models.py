from django.utils.translation import ugettext as _
from django.db import models


class EnabledManager(models.Manager):
    """Manager with enabled check"""

    def enabled(self):
        """Get enabled entries"""
        return self.filter(is_enabled=True)


class CarouselEntry(models.Model):
    """Carousel entry"""
    url = models.URLField(max_length=300, verbose_name=_('url'))
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    position = models.PositiveSmallIntegerField(
        default=0, verbose_name=_('position'),
    )
    title = models.CharField(max_length=300, verbose_name=_('title'))
    text = models.TextField(verbose_name=_('text'))
    image = models.ImageField(
        upload_to='carousel/%m/%d/', verbose_name=_('image'),
    )

    objects = EnabledManager()
    
    class Meta:
        verbose_name = _('carousel entry')
        verbose_name_plural = _('carousel entries')
        ordering = ('position',)

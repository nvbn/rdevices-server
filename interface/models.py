from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models


class NewsEntry(models.Model):
    """News entry"""
    slug = models.SlugField(verbose_name=_('slug'))
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    title = models.CharField(max_length=300, verbose_name=_('title'))
    preview = models.TextField(verbose_name=_('preview'))
    text = models.TextField(verbose_name=_('text'))
    
    class Meta:
        verbose_name = _('News entry')
        verbose_name_plural = _('News entries')


class CarouselEntry(models.Model):
    """Carousel entry"""
    url = models.URLField(max_length=300, verbose_name=_('url'))
    is_enabled = models.BooleanField(
        default=True, verbose_name=_('is enabled'),
    )
    title = models.CharField(max_length=300, verbose_name=_('title'))
    text = models.TextField(verbose_name=_('text'))
    image = models.ImageField(
        upload_to='carousel/%m/%d/', verbose_name=_('image'),
    )
    
    class Meta:
        verbose_name = _('carousel entry')
        verbose_name_plural = _('carousel entries')

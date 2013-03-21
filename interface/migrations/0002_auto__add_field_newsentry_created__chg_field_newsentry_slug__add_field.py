# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NewsEntry.created'
        db.add_column(u'interface_newsentry', 'created',
                      self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True),
                      keep_default=False)


        # Changing field 'NewsEntry.slug'
        db.alter_column(u'interface_newsentry', 'slug', self.gf('django_extensions.db.fields.AutoSlugField')(allow_duplicates=False, max_length=50, separator=u'-', populate_from='title', overwrite=False))
        # Adding field 'CarouselEntry.position'
        db.add_column(u'interface_carouselentry', 'position',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NewsEntry.created'
        db.delete_column(u'interface_newsentry', 'created')


        # Changing field 'NewsEntry.slug'
        db.alter_column(u'interface_newsentry', 'slug', self.gf('django.db.models.fields.SlugField')(max_length=50))
        # Deleting field 'CarouselEntry.position'
        db.delete_column(u'interface_carouselentry', 'position')


    models = {
        u'interface.carouselentry': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CarouselEntry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'})
        },
        u'interface.newsentry': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'NewsEntry'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'preview': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'allow_duplicates': 'False', 'max_length': '50', 'separator': "u'-'", 'blank': 'True', 'populate_from': "'title'", 'overwrite': 'False'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['interface']
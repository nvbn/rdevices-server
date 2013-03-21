# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NewsEntry'
        db.create_table(u'interface_newsentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('preview', self.gf('django.db.models.fields.TextField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'interface', ['NewsEntry'])

        # Adding model 'CarouselEntry'
        db.create_table(u'interface_carouselentry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=300)),
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal(u'interface', ['CarouselEntry'])


    def backwards(self, orm):
        # Deleting model 'NewsEntry'
        db.delete_table(u'interface_newsentry')

        # Deleting model 'CarouselEntry'
        db.delete_table(u'interface_carouselentry')


    models = {
        u'interface.carouselentry': {
            'Meta': {'object_name': 'CarouselEntry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '300'})
        },
        u'interface.newsentry': {
            'Meta': {'object_name': 'NewsEntry'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'preview': ('django.db.models.fields.TextField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['interface']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'CarouselEntry'
        db.delete_table(u'interface_carouselentry')


    def backwards(self, orm):
        # Adding model 'CarouselEntry'
        db.create_table(u'interface_carouselentry', (
            ('is_enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=300)),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'interface', ['CarouselEntry'])


    models = {
        
    }

    complete_apps = ['interface']
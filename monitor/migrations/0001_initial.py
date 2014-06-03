# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Team'
        db.create_table(u'monitor_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'monitor', ['Team'])

        # Adding model 'Words'
        db.create_table(u'monitor_words', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('word', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('nums', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'monitor', ['Words'])

        # Adding model 'AlarmRecord'
        db.create_table(u'monitor_alarmrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('user_name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('ip_and_port', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('word', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'monitor', ['AlarmRecord'])

        # Adding model 'Contact'
        db.create_table(u'monitor_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('recieve_email', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('recieve_sms', self.gf('django.db.models.fields.CharField')(max_length=8, null=True, blank=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitor.Team'], null=True, blank=True)),
        ))
        db.send_create_signal(u'monitor', ['Contact'])

        # Adding model 'Sites'
        db.create_table(u'monitor_sites', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['monitor.Team'], null=True, blank=True)),
        ))
        db.send_create_signal(u'monitor', ['Sites'])


    def backwards(self, orm):
        # Deleting model 'Team'
        db.delete_table(u'monitor_team')

        # Deleting model 'Words'
        db.delete_table(u'monitor_words')

        # Deleting model 'AlarmRecord'
        db.delete_table(u'monitor_alarmrecord')

        # Deleting model 'Contact'
        db.delete_table(u'monitor_contact')

        # Deleting model 'Sites'
        db.delete_table(u'monitor_sites')


    models = {
        u'monitor.alarmrecord': {
            'Meta': {'object_name': 'AlarmRecord'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_and_port': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'word': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'monitor.contact': {
            'Meta': {'object_name': 'Contact'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'recieve_email': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'recieve_sms': ('django.db.models.fields.CharField', [], {'max_length': '8', 'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Team']", 'null': 'True', 'blank': 'True'})
        },
        u'monitor.sites': {
            'Meta': {'object_name': 'Sites'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['monitor.Team']", 'null': 'True', 'blank': 'True'})
        },
        u'monitor.team': {
            'Meta': {'object_name': 'Team'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        u'monitor.words': {
            'Meta': {'object_name': 'Words'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nums': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        }
    }

    complete_apps = ['monitor']
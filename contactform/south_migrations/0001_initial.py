from south.db import db
from django.db import models
from contactform.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'ContactFormIntermediate'
        db.create_table('contactform_contactformintermediate', (
            ('cmsplugin_ptr', models.OneToOneField(orm['cms.CMSPlugin'])),
            ('form', models.ForeignKey(orm.ContactForm)),
        ))
        db.send_create_signal('contactform', ['ContactFormIntermediate'])
        
        # Adding model 'ContactFormSubmission'
        db.create_table('contactform_contactformsubmission', (
            ('id', models.AutoField(primary_key=True)),
            ('form', models.ForeignKey(orm.ContactForm)),
            ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ('sender_ip', models.IPAddressField()),
            ('form_url', models.URLField()),
            ('language', models.CharField(default='unknown', max_length=255)),
            ('form_data', models.TextField(null=True, blank=True)),
            ('form_data_pickle', PickledObjectField(null=True, editable=False, blank=True)),
        ))
        db.send_create_signal('contactform', ['ContactFormSubmission'])
        
        # Adding model 'Recipient'
        db.create_table('contactform_recipient', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField(max_length=100, blank=True)),
            ('email', models.EmailField()),
        ))
        db.send_create_signal('contactform', ['Recipient'])
        
        # Adding model 'ContactForm'
        db.create_table('contactform_contactform', (
            ('id', models.AutoField(primary_key=True)),
            ('language', models.CharField(_('language'), max_length=2)),
            ('name', models.CharField(_('name'), max_length=100)),
            ('description', models.TextField(_('description'), blank=True)),
            ('success_message', models.TextField(_('success message'), blank=True)),
            ('cc_managers', models.BooleanField(_('CC to managers'))),
            ('cc_site_contact', models.BooleanField(_('CC to site contact'))),
            ('has_captcha', models.BooleanField(_("has a captcha"), default=False)),
        ))
        db.send_create_signal('contactform', ['ContactForm'])
        
        # Adding model 'FormField'
        db.create_table('contactform_formfield', (
            ('id', models.AutoField(primary_key=True)),
            ('form', models.ForeignKey(orm.ContactForm, related_name='field_set')),
            ('label', models.CharField(max_length=255)),
            ('field_type', models.CharField(max_length=50)),
            ('widget', models.CharField(blank=True, max_length=50)),
            ('required', models.BooleanField()),
            ('position', models.IntegerField(default=1)),
        ))
        db.send_create_signal('contactform', ['FormField'])
        
        # Adding ManyToManyField 'ContactForm.recipients'
        db.create_table('contactform_contactform_recipients', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contactform', models.ForeignKey(orm.ContactForm, null=False)),
            ('recipient', models.ForeignKey(orm.Recipient, null=False))
        ))
        
        # Creating unique_together for [form, label] on FormField.
        db.create_unique('contactform_formfield', ['form_id', 'label'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'ContactFormIntermediate'
        db.delete_table('contactform_contactformintermediate')
        
        # Deleting model 'ContactFormSubmission'
        db.delete_table('contactform_contactformsubmission')
        
        # Deleting model 'Recipient'
        db.delete_table('contactform_recipient')
        
        # Deleting model 'ContactForm'
        db.delete_table('contactform_contactform')
        
        # Deleting model 'FormField'
        db.delete_table('contactform_formfield')
        
        # Dropping ManyToManyField 'ContactForm.recipients'
        db.delete_table('contactform_contactform_recipients')
        
        # Deleting unique_together for [form, label] on FormField.
        db.delete_unique('contactform_formfield', ['form_id', 'label'])
        
    
    
    models = {
        'cms.cmsplugin': {
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contactform.recipient': {
            'email': ('models.EmailField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'name': ('models.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'contactform.contactform': {
            'cc_managers': ('models.BooleanField', ["_('CC to managers')"], {}),
            'cc_site_contact': ('models.BooleanField', ["_('CC to site contact')"], {}),
            'description': ('models.TextField', ["_('description')"], {'blank': 'True'}),
            'has_captcha': ('models.BooleanField', ['_("has a captcha")'], {'default': 'False'}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'language': ('models.CharField', ["_('language')"], {'max_length': '2'}),
            'name': ('models.CharField', ["_('name')"], {'max_length': '100'}),
            'recipients': ('models.ManyToManyField', ["orm['contactform.Recipient']"], {}),
            'success_message': ('models.TextField', ["_('success message')"], {'blank': 'True'})
        },
        'cms.page': {
            'Meta': {'ordering': "('tree_id','lft')"},
            '_stub': True,
            'id': ('models.AutoField', [], {'primary_key': 'True'})
        },
        'contactform.contactformsubmission': {
            'Meta': {'ordering': '("-submitted_at",)'},
            'form': ('models.ForeignKey', ["orm['contactform.ContactForm']"], {}),
            'form_data': ('models.TextField', [], {'null': 'True', 'blank': 'True'}),
            'form_data_pickle': ('PickledObjectField', [], {'null': 'True', 'editable': 'False', 'blank': 'True'}),
            'form_url': ('models.URLField', [], {}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'language': ('models.CharField', [], {'default': "'unknown'", 'max_length': '255'}),
            'sender_ip': ('models.IPAddressField', [], {}),
            'submitted_at': ('models.DateTimeField', [], {'auto_now_add': 'True'})
        },
        'contactform.contactformintermediate': {
            'Meta': {'_bases': ['cms.models.CMSPlugin']},
            'cmsplugin_ptr': ('models.OneToOneField', ["orm['cms.CMSPlugin']"], {}),
            'form': ('models.ForeignKey', ["orm['contactform.ContactForm']"], {})
        },
        'contactform.formfield': {
            'Meta': {'ordering': "('position',)", 'unique_together': '(("form","label"),)'},
            'field_type': ('models.CharField', [], {'max_length': '50'}),
            'form': ('models.ForeignKey', ["orm['contactform.ContactForm']"], {'related_name': "'field_set'"}),
            'id': ('models.AutoField', [], {'primary_key': 'True'}),
            'label': ('models.CharField', [], {'max_length': '255'}),
            'position': ('models.IntegerField', [], {'default': '1'}),
            'required': ('models.BooleanField', [], {}),
            'widget': ('models.CharField', [], {'blank': 'True', 'max_length': '50'})
        }
    }
    
    complete_apps = ['contactform']

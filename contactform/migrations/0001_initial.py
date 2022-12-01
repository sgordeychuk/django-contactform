# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import contactform.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactForm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=15, verbose_name='language', choices=[(b'de', b'German')])),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('title', models.CharField(max_length=255, null=True, verbose_name='title', blank=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('submit_label', models.CharField(help_text='Standard: "absenden"', max_length=30, verbose_name='submit label', blank=True)),
                ('success_message', models.TextField(verbose_name='success message', blank=True)),
                ('cc_managers', models.BooleanField(help_text='Aktivieren um eine Kopie der Anfrage an die Site-Manager () zu senden.', verbose_name='CC to managers')),
                ('cc_site_contact', models.BooleanField(verbose_name='CC to site contact')),
                ('has_captcha', models.BooleanField(default=False, help_text='Should the user be required to fill up a captcha to verify he is human?', verbose_name='has a captcha')),
                ('css_class', models.CharField(max_length=255, null=True, verbose_name='CSS class', blank=True)),
                ('notification_email_subject', models.CharField(max_length=200, verbose_name='notification email subject', blank=True)),
                ('notification_email_body', models.TextField(verbose_name='notification email body', blank=True)),
                ('created_by', models.ForeignKey(blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'contact form',
                'verbose_name_plural': 'contact forms',
            },
        ),
        migrations.CreateModel(
            name='ContactFormIntermediate',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('form', models.ForeignKey(verbose_name='form', to='contactform.ContactForm')),
            ],
            options={
                'db_table': 'cmsplugin_contactformintermediate',
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='ContactFormSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted_at', models.DateTimeField(auto_now_add=True, verbose_name='submit date/time')),
                ('sender_ip', models.CharField(max_length=40, verbose_name='sender IP address')),
                ('form_url', models.URLField(verbose_name='form URL')),
                ('language', models.CharField(default=b'unknown', max_length=255, verbose_name='language')),
                ('form_data', models.TextField(null=True, verbose_name='form data', blank=True)),
                ('form_data_pickle', contactform.fields.PickledObjectField(verbose_name='form data pickle', null=True, editable=False, blank=True)),
                ('form', models.ForeignKey(to='contactform.ContactForm', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
                'ordering': ('-submitted_at',),
                'verbose_name': 'contact form submission',
                'verbose_name_plural': 'contact form submissions',
            },
        ),
        migrations.CreateModel(
            name='ContactFormSubmissionAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'private/contactform/submissions/%Y-%m-%d', max_length=200, verbose_name='file')),
                ('submission', models.ForeignKey(related_name='attachments', on_delete=django.db.models.deletion.PROTECT, verbose_name='submission', to='contactform.ContactFormSubmission')),
            ],
            options={
                'verbose_name': 'contact form submission attachment',
                'verbose_name_plural': 'contact form submission attachments',
            },
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, verbose_name='label')),
                ('field_type', models.CharField(max_length=100, verbose_name='field type', choices=[(b'django.forms.CharField', 'character field'), (b'django.forms.EmailField', 'email field'), (b'django.forms.BooleanField', 'checkbox'), (b'django.forms.ChoiceField', 'choice field'), (b'django.forms.FileField', 'file field'), (b'contactform.forms.EmailWithConfirmation', 'send confirmation to user email field'), (b'contactform.forms.EmailWithConfirmationCheckbox', 'send confirmation to user checkbox')])),
                ('widget', models.CharField(blank=True, max_length=50, verbose_name='widget', choices=[(b'django.forms.Textarea', 'textarea'), (b'django.forms.PasswordInput', 'password input'), (b'django.forms.RadioSelect', 'radio buttons')])),
                ('required', models.BooleanField(verbose_name='required')),
                ('initial', models.CharField(max_length=64, verbose_name='initial', blank=True)),
                ('empty_label', models.CharField(max_length=64, verbose_name='empty label', blank=True)),
                ('choices', models.TextField(help_text='enter choices divided by a semicolon (;) for ChoiceFields', null=True, verbose_name='choices', blank=True)),
                ('css_class', models.CharField(max_length=255, null=True, verbose_name='CSS class', blank=True)),
                ('position', models.IntegerField(default=1, verbose_name='position')),
                ('form', models.ForeignKey(related_name='field_set', on_delete=django.db.models.deletion.PROTECT, to='contactform.ContactForm')),
            ],
            options={
                'ordering': ('position',),
            },
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email')),
                ('added_by', models.ForeignKey(blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'recipient',
                'verbose_name_plural': 'recipients',
            },
        ),
        migrations.AddField(
            model_name='contactform',
            name='recipients',
            field=models.ManyToManyField(to='contactform.Recipient', verbose_name='recipients'),
        ),
        migrations.AddField(
            model_name='contactform',
            name='success_page',
            field=models.ForeignKey(blank=True, to='cms.Page', null=True),
        ),
    ]

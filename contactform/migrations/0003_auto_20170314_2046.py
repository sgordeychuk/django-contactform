# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contactform', '0002_auto_20161027_1348'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactform',
            name='has_recaptcha',
            field=models.BooleanField(default=False, help_text='Should the user be required to fill up a captcha to verify he is human?', verbose_name='has a reRECAPTCHA'),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='cc_managers',
            field=models.BooleanField(help_text='Aktivieren um eine Kopie der Anfrage an die Site-Manager (me@divio.ch) zu senden.', verbose_name='CC to managers'),
        ),
        migrations.AlterField(
            model_name='contactform',
            name='language',
            field=models.CharField(max_length=15, verbose_name='language', choices=[(b'de', 'German'), (b'en', 'English'), (b'fr', 'French'), (b'it', 'Italian')]),
        ),
        migrations.AlterField(
            model_name='formfield',
            name='field_type',
            field=models.CharField(max_length=100, verbose_name='field type', choices=[(b'django.forms.CharField', 'character field'), (b'django.forms.EmailField', 'email field'), (b'django.forms.BooleanField', 'checkbox'), (b'django.forms.ChoiceField', 'choice field'), (b'django.forms.FileField', 'file field'), (b'contactform.forms.EmailWithConfirmation', 'send confirmation to user email field'), (b'contactform.forms.EmailWithConfirmationCheckbox', 'send confirmation to user checkbox'), (b'django.forms.MultipleChoiceField', 'multiple choice field')]),
        ),
    ]

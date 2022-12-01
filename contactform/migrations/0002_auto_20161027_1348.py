# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contactform', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactform',
            name='success_page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cms.Page', null=True),
        ),
        migrations.AlterField(
            model_name='contactformintermediate',
            name='cmsplugin_ptr',
            field=models.OneToOneField(parent_link=True, related_name='contactform_contactformintermediate', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin'),
        ),
    ]

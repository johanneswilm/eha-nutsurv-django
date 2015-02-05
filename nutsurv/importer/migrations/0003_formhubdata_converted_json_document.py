# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20150121_2314'),
        ('importer', '0002_auto_20150204_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='formhubdata',
            name='converted_json_document',
            field=models.ForeignKey(blank=True, to='dashboard.JSONDocument', null=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20150312_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='json',
            field=jsonfield.fields.JSONField(help_text=b'A JSON document containing data for one alert.', null=True, blank=True),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_alert_json'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='category',
            field=models.CharField(default=b'general', max_length=255),
            preserve_default=True,
        ),
    ]

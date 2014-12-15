# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20141209_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 1, 1, 1, 1, 1), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='alert',
            name='last_modified',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 1, 1, 1, 1, 1), auto_now=True),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import dashboard.models
from django.utils.timezone import utc
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_auto_20150420_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdsurveyjson',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 15, 32, 23, 402377, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 15, 32, 25, 696853, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

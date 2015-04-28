# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import dashboard.models
from django.utils.timezone import utc
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_auto_20150420_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsurvey',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 15, 32, 28, 360883, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trainingsurvey',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 15, 32, 29, 994651, tzinfo=utc)),
            preserve_default=False,
        ),
    ]

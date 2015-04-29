# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0004_auto_20150420_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingsurvey',
            name='cluster',
            field=models.IntegerField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingsurvey',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingsurvey',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

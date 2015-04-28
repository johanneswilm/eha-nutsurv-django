# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0002_auto_20150420_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsurvey',
            name='cluster',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='trainingsurvey',
            name='cluster_name',
            field=models.CharField(max_length=30, blank=True),
            preserve_default=True,
        ),
    ]

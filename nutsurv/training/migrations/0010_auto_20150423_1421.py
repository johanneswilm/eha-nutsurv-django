# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0009_auto_20150421_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingsurvey',
            name='cluster_name',
            field=models.CharField(max_length=60, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingsurvey',
            name='first_admin_level',
            field=models.CharField(max_length=60, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingsurvey',
            name='second_admin_level',
            field=models.CharField(max_length=60, blank=True),
            preserve_default=True,
        ),
    ]

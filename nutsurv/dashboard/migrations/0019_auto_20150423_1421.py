# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_auto_20150421_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='cluster_name',
            field=models.CharField(max_length=60, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='first_admin_level',
            field=models.CharField(max_length=60, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='second_admin_level',
            field=models.CharField(max_length=60, blank=True),
            preserve_default=True,
        ),
    ]

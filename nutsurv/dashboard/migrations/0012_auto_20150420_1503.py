# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdsurveyjson',
            name='first_admin_level',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='second_admin_level',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='height',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='muac',
            field=models.SmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='weight',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
    ]

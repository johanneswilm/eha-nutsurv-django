# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20150416_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='householdmember',
            name='birthdate',
            field=models.DateField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='first_name',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='gender',
            field=models.CharField(blank=True, max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='index',
            field=models.SmallIntegerField(blank=True),
            preserve_default=True,
        ),
    ]

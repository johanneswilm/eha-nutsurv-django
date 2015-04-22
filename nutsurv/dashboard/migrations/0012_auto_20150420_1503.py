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
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='json',
            field=jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', validators=[dashboard.models.validate_json]),
            preserve_default=True,
        ),
    ]

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
            name='height',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='index',
            field=models.SmallIntegerField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='muac',
            field=models.SmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='householdmember',
            name='weight',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='json',
            field=jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', validators=[dashboard.models.validate_json]),
            preserve_default=True,
        ),
    ]

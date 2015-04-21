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
            name='json',
            field=jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', validators=[dashboard.models.validate_json]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingsurvey',
            name='start_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

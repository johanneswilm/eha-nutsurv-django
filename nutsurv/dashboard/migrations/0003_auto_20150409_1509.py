# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20150409_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='survey',
            field=models.ForeignKey(to='dashboard.HouseholdSurveyJSON', null=True),
            preserve_default=True,
        ),
    ]

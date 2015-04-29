# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0006_auto_20150420_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainingsurvey',
            name='team_lead',
        ),
    ]

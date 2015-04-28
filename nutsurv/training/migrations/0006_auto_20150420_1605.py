# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0005_auto_20150420_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingsurvey',
            name='cluster',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]

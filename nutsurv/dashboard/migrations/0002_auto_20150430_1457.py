# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_squashed_0023_auto_20150428_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdmember',
            name='extra_questions',
            field=django_pgjson.fields.JsonBField(default={}),
            preserve_default=True,
        ),
    ]

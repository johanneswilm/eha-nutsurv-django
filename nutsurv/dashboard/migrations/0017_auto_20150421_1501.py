# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_auto_20150420_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(default='POINT(0 0)', srid=4326),
            preserve_default=False,
        ),
    ]

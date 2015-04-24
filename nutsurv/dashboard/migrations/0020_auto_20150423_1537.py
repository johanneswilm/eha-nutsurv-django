# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0019_auto_20150423_1421'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='householdsurveyjson',
            name='point',
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True),
            preserve_default=True,
        ),
    ]

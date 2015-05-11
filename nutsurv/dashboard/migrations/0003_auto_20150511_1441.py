# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20150505_1309'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdsurveyjson',
            name='cluster_population',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='cluster_segment_population',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]

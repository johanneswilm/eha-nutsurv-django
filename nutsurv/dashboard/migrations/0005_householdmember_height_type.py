# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20150515_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='householdmember',
            name='height_type',
            field=models.CharField(blank=True, max_length=10, choices=[(b'recumbent', b'Recumbent'), (b'standing', b'Standing')]),
        ),
    ]

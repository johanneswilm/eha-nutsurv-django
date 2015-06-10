# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_auto_20150511_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsubject',
            name='height_type',
            field=models.CharField(blank=True, max_length=10, choices=[(b'recumbent', b'Recumbent'), (b'standing', b'Standing')]),
        ),
    ]

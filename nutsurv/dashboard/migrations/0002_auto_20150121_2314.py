# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_squashed_0014_auto_20150119_2244'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='collectabledata',
            name='uniqueactivenameddocument_ptr',
        ),
        migrations.DeleteModel(
            name='CollectableData',
        ),
        migrations.AlterField(
            model_name='alert',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='alert',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

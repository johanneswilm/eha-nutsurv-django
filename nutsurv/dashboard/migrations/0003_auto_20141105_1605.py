# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_jsondocumenttype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jsondocumenttype',
            name='priority',
            field=models.IntegerField(default=10, unique=True, null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]

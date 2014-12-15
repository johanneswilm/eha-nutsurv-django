# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20141105_1605'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('archived', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='jsondocumenttype',
            name='priority',
            field=models.IntegerField(null=True, default=10, validators=[django.core.validators.MinValueValidator(0)], blank=True, help_text=b'Leave empty for the lowest priority', unique=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='trainingsurvey',
            name='first_admin_level',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='trainingsurvey',
            name='second_admin_level',
            field=models.CharField(max_length=20, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingroommember',
            name='height',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingroommember',
            name='muac',
            field=models.SmallIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='trainingroommember',
            name='weight',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
    ]

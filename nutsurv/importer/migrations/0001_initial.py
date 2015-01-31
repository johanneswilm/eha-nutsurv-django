# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FormhubData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contents', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('uuid', models.CharField(unique=True, max_length=256)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

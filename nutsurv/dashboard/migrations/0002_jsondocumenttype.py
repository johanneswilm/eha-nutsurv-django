# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JSONDocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('schema', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('priority', models.IntegerField(unique=True, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

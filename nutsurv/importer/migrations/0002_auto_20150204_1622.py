# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FakeTeams',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contents', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('team_id', models.IntegerField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='formhubdata',
            options={'verbose_name_plural': 'Formhub Data Entries'},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20150202_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='FakeTeams',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('team_id', models.IntegerField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormhubSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('uuid', models.CharField(unique=True, max_length=256)),
                ('converted_household_survey', models.ForeignKey(blank=True, to='dashboard.HouseholdSurveyJSON', null=True)),
            ],
            options={
                'verbose_name_plural': 'Formhub Data Entries',
            },
            bases=(models.Model,),
        ),
    ]

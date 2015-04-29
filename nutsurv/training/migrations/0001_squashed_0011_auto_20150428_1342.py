# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models
from django.conf import settings


class Migration(migrations.Migration):

    replaces = [(b'training', '0001_initial'), (b'training', '0002_auto_20150420_1503'), (b'training', '0003_auto_20150420_1512'), (b'training', '0004_auto_20150420_1532'), (b'training', '0005_auto_20150420_1604'), (b'training', '0006_auto_20150420_1605'), (b'training', '0007_auto_20150421_1047'), (b'training', '0008_auto_20150421_1501'), (b'training', '0009_auto_20150421_1508'), (b'training', '0010_auto_20150423_1421'), (b'training', '0011_auto_20150428_1342')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0001_squashed_0023_auto_20150428_1542'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingSubject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(blank=True, max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')])),
                ('first_name', models.TextField(blank=True)),
                ('index', models.SmallIntegerField(blank=True)),
                ('birthdate', models.DateField(null=True, blank=True)),
                ('muac', models.SmallIntegerField(null=True)),
                ('weight', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('edema', models.NullBooleanField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrainingSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('household_number', models.SmallIntegerField()),
                ('json', jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.')),
                ('second_admin_level', models.CharField(max_length=60, blank=True)),
                ('first_admin_level', models.CharField(max_length=60, blank=True)),
                ('cluster', models.IntegerField(null=True, blank=True)),
                ('cluster_name', models.CharField(max_length=60, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('end_time', models.DateTimeField(null=True, blank=True)),
                ('uuid', models.CharField(help_text=b'A unique identifier of an individual household survey.  Typically assigned by a mobile application before the data is uploaded to the server.  If in doubt, do no edit.', unique=True, max_length=255)),
                ('team_anthropometrist', models.ForeignKey(related_name='trainingsurvey_surveys_as_team_anthropometrist', to='dashboard.TeamMember')),
                ('team_assistant', models.ForeignKey(related_name='trainingsurvey_surveys_as_team_assistant', to='dashboard.TeamMember')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'household survey',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trainingsubject',
            name='household_survey',
            field=models.ForeignKey(related_name='members', to='training.TrainingSurvey'),
            preserve_default=True,
        ),
    ]

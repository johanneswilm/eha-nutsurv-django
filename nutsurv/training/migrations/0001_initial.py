# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import dashboard.models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20150420_1222'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingRoom',
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
            name='TrainingRoomMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(blank=True, max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')])),
                ('first_name', models.TextField(blank=True)),
                ('index', models.SmallIntegerField(blank=True)),
                ('birthdate', models.DateField(null=True, blank=True)),
                ('muac', models.SmallIntegerField()),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
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
                ('json', jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', validators=[dashboard.models.validate_json])),
                ('uuid', models.CharField(help_text=b'A unique identifier of an individual household survey.  Typically assigned by a mobile application before the data is uploaded to the server.  If in doubt, do no edit.', unique=True, max_length=255)),
                ('team_anthropometrist', models.ForeignKey(related_name='trainingsurvey_surveys_as_team_anthropometrist', to='dashboard.TeamMember')),
                ('team_assistant', models.ForeignKey(related_name='trainingsurvey_surveys_as_team_assistant', to='dashboard.TeamMember')),
                ('team_lead', models.ForeignKey(related_name='trainingsurvey_as_team_lead', to='dashboard.TeamMember')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'household survey',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trainingroommember',
            name='household_survey',
            field=models.ForeignKey(related_name='members', to='training.TrainingSurvey'),
            preserve_default=True,
        ),
    ]

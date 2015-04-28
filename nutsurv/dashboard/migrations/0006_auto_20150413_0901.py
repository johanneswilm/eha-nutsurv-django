# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20150409_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseholdMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(max_length=1, choices=[(b'M', b'Male'), (b'F', b'Female'), (b'O', b'Other')])),
                ('firstName', models.TextField()),
                ('index', models.SmallIntegerField()),
                ('muac', models.SmallIntegerField(null=True)),
                ('birthdate', models.DateField()),
                ('weight', models.FloatField(null=True)),
                ('height', models.FloatField(null=True)),
                ('edema', models.NullBooleanField()),
                ('household_survey', models.ForeignKey(related_name='members', to='dashboard.HouseholdSurveyJSON')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='household_number',
            field=models.SmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='team_anthropometrist',
            field=models.ForeignKey(related_name='householdsurveyjson_surveys_as_team_anthropometrist', to='dashboard.TeamMember'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='team_assistant',
            field=models.ForeignKey(related_name='householdsurveyjson_surveys_as_team_assistant', to='dashboard.TeamMember'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='team_lead',
            field=models.ForeignKey(related_name='householdsurveyjson_as_team_lead', to='dashboard.TeamMember'),
            preserve_default=True,
        ),
    ]

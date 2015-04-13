# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import phonenumber_field.modelfields
import dashboard.models
import django.contrib.gis.db.models.fields
import django.utils.timezone
import dashboard.fields
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('json', jsonfield.fields.JSONField(
                    help_text=b'A JSON document containing data for one alert.', null=True, blank=True)),
                ('category', models.CharField(default=b'general', max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_0', models.CharField(
                    help_text=b'The area two levels higher than this one (i.e. the area containing the area which contains this area (e.g. the name of a country))', max_length=255)),
                ('name_1', models.CharField(
                    help_text=b'The area one level higher than this one (i.e. the area containing this area (e.g. the name of a 1st Admin))', max_length=255)),
                ('name_2', models.CharField(
                    help_text=b'The name of this area (e.g. the name of an 2nd Admin))', max_length=255)),
                ('varname_2', models.CharField(
                    help_text=b'Alternative name for this area (optional, can be left blank)', max_length=255, blank=True)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(
                    help_text=b'A multi-polygon field defining boundaries of this area', srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Clusters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(
                    default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1,
                                                help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default={
                }, help_text='Please enter the JSON structure describing all the clusters for the planned survey.', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClustersPerFirstAdminLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(
                    default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1,
                                                help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default={
                }, help_text='Please enter the JSON structure defining the number of standard and reserve clusters per 1st Admin.  E.g.: { "first_admin_levels": { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { "standard": 7, "reserve": 3 } } }', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FirstAdminLevels',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(
                    default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1,
                                                help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(
                    default=[], help_text='Please enter the JSON structure defining the 1st Admin area data.', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FirstAdminLevelsReserveClusters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(
                    default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1,
                                                help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default=[
                ], help_text='Please enter the JSON structure describing the 1st Admin with reserve clusters enabled.', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HouseholdSurveyJSON',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField(
                    help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', validators=[dashboard.models.validate_json])),
                ('uuid', models.CharField(
                    help_text=b'A unique identifier of an individual household survey.  Typically assigned by a mobile application before the data is uploaded to the server.  If in doubt, do no edit.', unique=True, max_length=255)),
            ],
            options={
                'verbose_name': 'household survey',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireSpecification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(
                    default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1,
                                                help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('specification', models.TextField(
                    help_text='Please enter or copy & paste your new questionnaire specification written in the QSL (Questionnaire Specification Language). <br />Please pay particular attention to indentation as indentation levels are part of the QSL and incorrect indentation will most likely produce nonsensical specification.<br />To familiarise yourself with the version of QSL used here please read <a href="/static/qsl.html" target="_blank">this document</a>.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SecondAdminLevel',
            fields=[
                ('area_ptr', models.OneToOneField(
                    parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.Area')),
            ],
            options={
            },
            bases=('dashboard.area',),
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member_id', django_extensions.db.fields.AutoSlugField(
                    editable=False, populate_from=b'random_id', separator=b'', blank=True, unique=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('mobile', phonenumber_field.modelfields.PhoneNumberField(max_length=128, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('birth_year', models.IntegerField()),
                ('gender', models.CharField(blank=True, max_length=3, choices=[(b'M', 'Male'), (b'F', 'Female')])),
                ('created', django_extensions.db.fields.CreationDateTimeField(
                    default=django.utils.timezone.now, editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(
                    default=django.utils.timezone.now, editable=False, blank=True)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='team_anthropometrist',
            field=models.ForeignKey(related_name='surveys_as_team_anthropometrist', to='dashboard.TeamMember'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='team_assistant',
            field=models.ForeignKey(related_name='surveys_as_team_assistant', to='dashboard.TeamMember'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='householdsurveyjson',
            name='team_lead',
            field=models.ForeignKey(related_name='surveys_as_team_lead', to='dashboard.TeamMember'),
            preserve_default=True,
        ),
    ]

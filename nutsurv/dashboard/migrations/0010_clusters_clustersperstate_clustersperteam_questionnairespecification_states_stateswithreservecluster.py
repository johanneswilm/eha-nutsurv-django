# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_auto_20150317_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clusters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1, help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default={}, help_text='Please enter the JSON structure describing all the clusters for the planned survey.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'The "Clusters" documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClustersPerState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1, help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default={}, help_text='Please enter the JSON structure defining the number of standard and reserve clusters per 1st Admin.  E.g.: { "states": { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { "standard": 7, "reserve": 3 } } }', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'The "Clusters per 1st Admin" documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClustersPerTeam',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1, help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default={}, help_text='Please enter the JSON structure defining the (planned) number of clusters per each team.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'The "Clusters per Team" documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireSpecification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1, help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('specification', models.TextField(help_text='Please enter or copy & paste your new questionnaire specification written in the QSL (Questionnaire Specification Language). <br />Please pay particular attention to indentation as indentation levels are part of the QSL and incorrect indentation will most likely produce nonsensical specification.<br />To familiarise yourself with the version of QSL used here please read <a href="/static/qsl.html" target="_blank">this document</a>.')),
            ],
            options={
                'verbose_name_plural': 'The "Questionnaire Specification" documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='States',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1, help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default=[], help_text='Please enter the JSON structure defining the 1st Admin area data.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'The "1st Admin" documents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatesWithReserveClusters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name_or_id', models.CharField(default=uuid.uuid1, help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
                ('json', jsonfield.fields.JSONField(default=[], help_text='Please enter the JSON structure describing the 1st Admin with reserve clusters enabled.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'The "1st Admin with Reserve Clusters" documents',
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.fields
import datetime
import django.contrib.gis.db.models.fields
import django.core.validators


class Migration(migrations.Migration):

    replaces = [(b'dashboard', '0001_initial'), (b'dashboard', '0002_jsondocumenttype'), (b'dashboard', '0003_auto_20141105_1605'), (b'dashboard', '0004_auto_20141209_1148'), (b'dashboard', '0005_auto_20141209_1449'), (b'dashboard', '0006_clustersjson'), (b'dashboard', '0007_area_lga'), (b'dashboard', '0008_auto_20150101_0237'), (b'dashboard', '0009_questionnairespecification'), (b'dashboard', '0010_auto_20150116_2351'), (b'dashboard', '0011_clustersperstate_collectabledata_uniqueactivedocument_uniqueactivenameddocument'), (b'dashboard', '0012_auto_20150119_1642'), (b'dashboard', '0013_clustersperteam'), (b'dashboard', '0014_auto_20150119_2244')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JSONDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JSONDocumentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('schema', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('priority', models.IntegerField(null=True, default=10, validators=[django.core.validators.MinValueValidator(0)], blank=True, help_text=b'Leave empty for the lowest priority', unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('archived', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=datetime.datetime(1, 1, 1, 1, 1, 1, 1), auto_now_add=True)),
                ('last_modified', models.DateTimeField(default=datetime.datetime(1, 1, 1, 1, 1, 1, 1), auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ClustersJSON',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField(help_text=b' ', null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_0', models.CharField(max_length=255)),
                ('name_1', models.CharField(max_length=255)),
                ('name_2', models.CharField(max_length=255)),
                ('varname_2', models.CharField(max_length=255)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LGA',
            fields=[
                ('area_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.Area')),
            ],
            options={
            },
            bases=('dashboard.area',),
        ),
        migrations.AlterField(
            model_name='area',
            name='mpoly',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(help_text=b'A multi-polygon field defining boundaries of this area', srid=4326),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_0',
            field=models.CharField(help_text=b'The area two levels higher than this one (i.e. the area containing the area which contains this area (e.g. the name of a country))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_1',
            field=models.CharField(help_text=b'The area one level higher than this one (i.e. the area containing this area (e.g. the name of a state))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_2',
            field=models.CharField(help_text=b'The name of this area (e.g. the name of an LGA))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='varname_2',
            field=models.CharField(help_text=b'Alternative name for this area (optional, can be left blank)', max_length=255, blank=True),
        ),
        migrations.CreateModel(
            name='QuestionnaireSpecification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_or_id', models.CharField(help_text='Please enter a unique name or id of your new questionnaire specification.', unique=True, max_length=255)),
                ('specification', models.TextField(help_text='Please enter or copy & paste your new questionnaire specification written in the QSL (Questionnaire Specification Language). <br />Please pay particular attention to indentation as indentation levels are part of the QSL and incorrect indentation will most likely produce nonsensical specification.<br />To familiarise yourself with the version of QSL used here please read <a href="/static/qsl.html" target="_blank">this document</a>.')),
                ('active', dashboard.fields.MaxOneActiveQuestionnaireField(default=False, help_text='Activate this questionnaire specification.  Only one questionnaire specification may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UniqueActiveDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', dashboard.fields.UniqueActiveField(default=False, help_text='Activate this document.  Only one document of this type may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UniqueActiveNamedDocument',
            fields=[
                ('uniqueactivedocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveDocument')),
                ('name_or_id', models.CharField(help_text='Please enter a unique name or id of your new document.', unique=True, max_length=255)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivedocument',),
        ),
        migrations.CreateModel(
            name='CollectableData',
            fields=[
                ('uniqueactivenameddocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveNamedDocument')),
                ('json', jsonfield.fields.JSONField(default=b'\n        For example:\n        {\n            "collectable_data": {\n                "women": [\n                    "breastfeeding",\n                    "muac",\n                    "height",\n                    "weight",\n                    "pregnant",\n                    "ante-natal_care",\n                    "ever_pregnant"\n                ],\n                "children": [\n                    "muac",\n                    "weight",\n                    "heightType",\n                    "edema",\n                    "birthDate",\n                    "height",\n                    "diarrhoea"\n                ]\n            }\n        }\n        ', help_text='Please enter the JSON structure defining the collectable data.', null=True, blank=True)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
        migrations.CreateModel(
            name='ClustersPerState',
            fields=[
                ('uniqueactivenameddocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveNamedDocument')),
                ('json', jsonfield.fields.JSONField(default=b'\n            For example:\n\n            {\n                "states": {\n                    "Kano": {\n                        "standard": 5,\n                        "reserve": 3\n                        },\n                    "Lagos": {\n                        "standard": 7,\n                        "reserve": 3\n                        },\n                    "Kaduna": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Katsina": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Oyo": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Rivers": {\n                        "standard": 6,\n                        "reserve": 3\n                        },\n                    "Bauchi": {\n                        "standard": 3,\n                        "reserve": 3\n                        },\n                    "Jigawa": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Benue": {\n                        "standard": 9,\n                        "reserve": 3\n                        },\n                    "Anambra": {\n                        "standard": 10,\n                        "reserve": 3\n                        },\n                    "Borno": {\n                        "standard": 11,\n                        "reserve": 3\n                        },\n                    "Delta": {\n                        "standard": 12,\n                        "reserve": 3\n                        },\n                    "Imo": {\n                        "standard": 13,\n                        "reserve": 3\n                        },\n                    "Niger": {\n                        "standard": 14,\n                        "reserve": 3\n                        },\n                    "Akwa Ibom": {\n                        "standard": 11,\n                        "reserve": 3\n                        },\n                    "Ogun": {\n                        "standard": 10,\n                        "reserve": 3\n                        },\n                    "Sokoto": {\n                        "standard": 3,\n                        "reserve": 3\n                        },\n                    "Ondo": {\n                        "standard": 20,\n                        "reserve": 3\n                        },\n                    "Osun": {\n                        "standard": 1,\n                        "reserve": 3\n                        },\n                    "Kogi": {\n                        "standard": 7,\n                        "reserve": 3\n                        },\n                    "Zamfara": {\n                        "standard": 6,\n                        "reserve": 3\n                        },\n                    "Enugu": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Kebbi": {\n                        "standard": 9,\n                        "reserve": 3\n                        },\n                    "Edo": {\n                        "standard": 7,\n                        "reserve": 2\n                        },\n                    "Plateau": {\n                        "standard": 10,\n                        "reserve": 4\n                        },\n                    "Adamawa": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Cross River": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Abia": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Ekiti": {\n                        "standard": 12,\n                        "reserve": 5\n                        },\n                    "Kwara": {\n                        "standard": 15,\n                        "reserve": 6\n                        },\n                    "Gombe": {\n                        "standard": 7,\n                        "reserve": 3\n                        },\n                    "Yobe": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Taraba": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Ebonyi": {\n                        "standard": 12,\n                        "reserve": 3\n                        },\n                    "Nasarawa": {\n                        "standard": 13,\n                        "reserve": 3\n                        },\n                    "Bayelsa": {\n                        "standard": 14,\n                        "reserve": 3\n                        },\n                    "Abuja Federal Capital Territory": {\n                        "standard": 30,\n                        "reserve": 3\n                        }\n                }\n            }\n        ', help_text='Please enter the JSON structure defining the number of standard and reserve clusters per state.  E.g.: { "states": { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { "standard": 7, "reserve": 3 } } }', null=True, blank=True)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
        migrations.CreateModel(
            name='States',
            fields=[
                ('uniqueactivenameddocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveNamedDocument')),
                ('json', jsonfield.fields.JSONField(default=b'\n            For example:\n\n            {\n                "states": ["Kano", "Lagos", "Kaduna",\n                    "Katsina", "Oyo", "Rivers",\n                    "Bauchi", "Jigawa", "Benue",\n                    "Anambra", "Borno", "Delta",\n                    "Imo", "Niger", "Akwa Ibom",\n                    "Ogun", "Sokoto", "Ondo",\n                    "Osun", "Kogi", "Zamfara",\n                    "Enugu", "Kebbi", "Edo",\n                    "Plateau", "Adamawa",\n                    "Cross River", "Abia",\n                    "Ekiti", "Kwara", "Gombe",\n                    "Yobe", "Taraba", "Ebonyi",\n                    "Nasarawa", "Bayelsa",\n                    "Abuja Federal Capital Territory"\n                ]\n            }\n        ', help_text='Please enter the JSON structure defining the states data.', null=True, blank=True)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
        migrations.CreateModel(
            name='StatesWithReserveClusters',
            fields=[
                ('uniqueactivenameddocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveNamedDocument')),
                ('json', jsonfield.fields.JSONField(default=b'\n            For example:\n\n            {\n                "states": [\n                            "Kano",\n                            "Gombe",\n                            "Yobe",\n                            "Abuja Federal Capital Territory"\n                ]\n            }\n        ', help_text='Please enter the JSON structure describing the states with reserve clusters.', null=True, blank=True)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
        migrations.CreateModel(
            name='ClustersPerTeam',
            fields=[
                ('uniqueactivenameddocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveNamedDocument')),
                ('json', jsonfield.fields.JSONField(default=b'\n            For example:\n\n            {\n                "teams": {\n                    "1": 5,\n                    "2": 15,\n                    "3": 17\n                }\n            }\n        ', help_text='Please enter the JSON structure defining the number of clusters per each team.', null=True, blank=True)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
        migrations.AlterModelOptions(
            name='clustersjson',
            options={'verbose_name_plural': 'The "Clusters" JSON documents'},
        ),
        migrations.AlterModelOptions(
            name='clustersperstate',
            options={'verbose_name_plural': 'The "Clusters per State" documents'},
        ),
        migrations.AlterModelOptions(
            name='clustersperteam',
            options={'verbose_name_plural': 'The "Clusters per Team" documents'},
        ),
        migrations.AlterModelOptions(
            name='collectabledata',
            options={'verbose_name_plural': 'The "Collectable Data" documents'},
        ),
        migrations.AlterModelOptions(
            name='jsondocument',
            options={'verbose_name_plural': 'JSON documents'},
        ),
        migrations.AlterModelOptions(
            name='jsondocumenttype',
            options={'verbose_name_plural': 'JSON document types'},
        ),
        migrations.AlterModelOptions(
            name='lga',
            options={'verbose_name': 'LGA'},
        ),
        migrations.AlterModelOptions(
            name='questionnairespecification',
            options={'verbose_name_plural': 'The "Questionnaire Specification" documents'},
        ),
        migrations.AlterModelOptions(
            name='states',
            options={'verbose_name_plural': 'The "States" documents'},
        ),
        migrations.AlterModelOptions(
            name='stateswithreserveclusters',
            options={'verbose_name_plural': 'The "States with Reserve Clusters" documents'},
        ),
        migrations.AlterField(
            model_name='clustersjson',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n        For example:\n\n        {\n            "clusters": {\n                "723": {\n                    "cluster_name": "Share",\n                    "lga_name": "Ifelodun",\n                    "state_name": "Kwara"\n                },\n                "318": {\n                    "cluster_name": "Emadadja",\n                    "lga_name": "Udu",\n                    "state_name": "Delta"\n                }\n            }\n        }\n        ', help_text='Please enter the JSON structure describing all the clusters for the planned survey.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='clustersperstate',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n            For example:\n\n            {\n                    "Kano": {\n                        "standard": 5,\n                        "reserve": 3\n                        },\n                    "Lagos": {\n                        "standard": 7,\n                        "reserve": 3\n                        },\n                    "Kaduna": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Katsina": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Oyo": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Rivers": {\n                        "standard": 6,\n                        "reserve": 3\n                        },\n                    "Bauchi": {\n                        "standard": 3,\n                        "reserve": 3\n                        },\n                    "Jigawa": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Benue": {\n                        "standard": 9,\n                        "reserve": 3\n                        },\n                    "Anambra": {\n                        "standard": 10,\n                        "reserve": 3\n                        },\n                    "Borno": {\n                        "standard": 11,\n                        "reserve": 3\n                        },\n                    "Delta": {\n                        "standard": 12,\n                        "reserve": 3\n                        },\n                    "Imo": {\n                        "standard": 13,\n                        "reserve": 3\n                        },\n                    "Niger": {\n                        "standard": 14,\n                        "reserve": 3\n                        },\n                    "Akwa Ibom": {\n                        "standard": 11,\n                        "reserve": 3\n                        },\n                    "Ogun": {\n                        "standard": 10,\n                        "reserve": 3\n                        },\n                    "Sokoto": {\n                        "standard": 3,\n                        "reserve": 3\n                        },\n                    "Ondo": {\n                        "standard": 20,\n                        "reserve": 3\n                        },\n                    "Osun": {\n                        "standard": 1,\n                        "reserve": 3\n                        },\n                    "Kogi": {\n                        "standard": 7,\n                        "reserve": 3\n                        },\n                    "Zamfara": {\n                        "standard": 6,\n                        "reserve": 3\n                        },\n                    "Enugu": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Kebbi": {\n                        "standard": 9,\n                        "reserve": 3\n                        },\n                    "Edo": {\n                        "standard": 7,\n                        "reserve": 2\n                        },\n                    "Plateau": {\n                        "standard": 10,\n                        "reserve": 4\n                        },\n                    "Adamawa": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Cross River": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Abia": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Ekiti": {\n                        "standard": 12,\n                        "reserve": 5\n                        },\n                    "Kwara": {\n                        "standard": 15,\n                        "reserve": 6\n                        },\n                    "Gombe": {\n                        "standard": 7,\n                        "reserve": 3\n                        },\n                    "Yobe": {\n                        "standard": 8,\n                        "reserve": 3\n                        },\n                    "Taraba": {\n                        "standard": 15,\n                        "reserve": 3\n                        },\n                    "Ebonyi": {\n                        "standard": 12,\n                        "reserve": 3\n                        },\n                    "Nasarawa": {\n                        "standard": 13,\n                        "reserve": 3\n                        },\n                    "Bayelsa": {\n                        "standard": 14,\n                        "reserve": 3\n                        },\n                    "Abuja Federal Capital Territory": {\n                        "standard": 30,\n                        "reserve": 3\n                        }\n            }\n        ', help_text='Please enter the JSON structure defining the number of standard and reserve clusters per state.  E.g.: { "states": { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { "standard": 7, "reserve": 3 } } }', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='clustersperteam',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n            For example:\n\n            {\n                "1": 5,\n                "2": 15,\n                "3": 17\n            }\n        ', help_text='Please enter the JSON structure defining the (planned) number of clusters per each team.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='collectabledata',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n        For example:\n        {\n                "women": [\n                    "breastfeeding",\n                    "muac",\n                    "height",\n                    "weight",\n                    "pregnant",\n                    "ante-natal_care",\n                    "ever_pregnant"\n                ],\n                "children": [\n                    "muac",\n                    "weight",\n                    "heightType",\n                    "edema",\n                    "birthDate",\n                    "height",\n                    "diarrhoea"\n                ]\n        }\n        ', help_text='Please enter the JSON structure defining the collectable data.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='states',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n            For example:\n\n            [\n                "Kano", "Lagos", "Kaduna",\n                "Katsina", "Oyo", "Rivers",\n                "Bauchi", "Jigawa", "Benue",\n                "Anambra", "Borno", "Delta",\n                "Imo", "Niger", "Akwa Ibom",\n                "Ogun", "Sokoto", "Ondo",\n                "Osun", "Kogi", "Zamfara",\n                "Enugu", "Kebbi", "Edo",\n                "Plateau", "Adamawa",\n                "Cross River", "Abia",\n                "Ekiti", "Kwara", "Gombe",\n                "Yobe", "Taraba", "Ebonyi",\n                "Nasarawa", "Bayelsa",\n                "Abuja Federal Capital Territory"\n            ]\n        ', help_text='Please enter the JSON structure defining the states data.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='stateswithreserveclusters',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n            For example:\n\n            [\n                "Kano",\n                "Gombe",\n                "Yobe",\n                "Abuja Federal Capital Territory"\n            ]\n        ', help_text='Please enter the JSON structure describing the states with reserve clusters.', null=True, blank=True),
        ),
    ]

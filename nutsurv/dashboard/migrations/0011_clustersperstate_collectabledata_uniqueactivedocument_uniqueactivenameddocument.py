# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_auto_20150116_2351'),
    ]

    operations = [
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
                ('json', jsonfield.fields.JSONField(help_text='Please enter the JSON structure defining the number of standard and reserve clusters per state.  E.g.: { "states": { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { "standard": 7, "reserve": 3 } } }', null=True, blank=True)),
            ],
            options={
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
    ]

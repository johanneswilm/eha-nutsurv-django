# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0013_clustersperteam'),
    ]

    operations = [
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

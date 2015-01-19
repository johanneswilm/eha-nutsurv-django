# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_auto_20150119_1642'),
    ]

    operations = [
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
    ]

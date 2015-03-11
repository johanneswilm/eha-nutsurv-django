# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20150202_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stateswithreserveclusters',
            name='json',
            field=jsonfield.fields.JSONField(default=b'\n            For example:\n\n            [\n                "Kano",\n                "Gombe",\n                "Yobe",\n                "Abuja Federal Capital Territory"\n            ]\n        ', help_text='Please enter the JSON structure describing the states with reserve clusters enabled.', null=True, blank=True),
        ),
    ]

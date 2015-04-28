# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0011_auto_20150428_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingsurvey',
            name='json',
            field=jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.'),
            preserve_default=True,
        ),
    ]

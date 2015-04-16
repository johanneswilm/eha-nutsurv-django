# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import django_extensions.db.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='householdsurveyjson',
            name='json',
            field=jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', validators=[dashboard.models.validate_json]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='teammember',
            name='member_id',
            field=django_extensions.db.fields.AutoSlugField(editable=False, populate_from=b'id', separator=b'', blank=True, unique=True),
            preserve_default=True,
        ),
    ]

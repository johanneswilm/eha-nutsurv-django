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
            model_name='teammember',
            name='member_id',
            field=django_extensions.db.fields.AutoSlugField(editable=False, populate_from=b'id', separator=b'', blank=True, unique=True),
            preserve_default=True,
        ),
    ]

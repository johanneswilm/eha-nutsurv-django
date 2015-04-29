# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teammember',
            name='member_id',
        ),
    ]

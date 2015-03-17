# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.fields
import uuid

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20150317_0945'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UniqueActiveNamedDocument',
        ),
        migrations.DeleteModel(
            name='UniqueActiveDocument',
        ),
    ]

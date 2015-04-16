# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import dashboard.models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_auto_20150413_0901'),
    ]

    operations = [
        migrations.RenameField(
            model_name='householdmember',
            old_name='firstName',
            new_name='first_name',
        ),
    ]

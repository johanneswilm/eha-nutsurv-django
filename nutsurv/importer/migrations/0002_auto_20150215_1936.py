# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formhubsurvey',
            options={'verbose_name_plural': 'Formhub Survey Entries'},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dashboard.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_questionnairespecification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnairespecification',
            name='active',
            field=dashboard.fields.MaxOneActiveQuestionnaireField(default=False, help_text='Activate this questionnaire specification.  Only one questionnaire specification may be active at any given time.'),
        ),
    ]

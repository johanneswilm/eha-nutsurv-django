# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dashboard.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_alert_category'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Clusters',
        ),
        migrations.DeleteModel(
            name='QuestionnaireSpecification',
        ),
        migrations.DeleteModel(
            name='ClustersPerState',
        ),
        migrations.DeleteModel(
            name='States',
        ),
        migrations.DeleteModel(
            name='StatesWithReserveClusters',
        ),
        migrations.DeleteModel(
            name='ClustersPerTeam',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20150121_2314'),
    ]

    operations = [
        migrations.CreateModel(
            name='HouseholdSurveyJSON',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', jsonfield.fields.JSONField(help_text=b'A JSON document containing data acquired from one household.  Typically not edited here but uploaded from a mobile application used by a team of surveyors in the field.  If in doubt, do not edit.', null=True, blank=True)),
                ('uuid', models.CharField(help_text=b'A unique identifier of an individual household survey.  Typically assigned by a mobile application before the data is uploaded to the server.  If in doubt, do no edit.', unique=True, max_length=255)),
            ],
            options={
                'verbose_name': 'household survey',
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='JSONDocument',
        ),
        migrations.DeleteModel(
            name='JSONDocumentType',
        ),
    ]

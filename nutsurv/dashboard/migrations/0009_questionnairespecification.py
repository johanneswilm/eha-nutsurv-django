# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20150101_0237'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionnaireSpecification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_or_id', models.CharField(help_text='Please enter a unique name or id of your new questionnaire specification.', unique=True, max_length=255)),
                ('specification', models.TextField(help_text='Please enter or copy & paste your new questionnaire specification written in the QSL (Questionnaire Specification Language). <br />Please pay particular attention to indentation as indentation levels are part of the QSL and incorrect indentation will most likely produce nonsensical specification.<br />To familiarise yourself with the version of QSL used here please read <a href="/static/qsl.html" target="_blank">this document</a>.')),
                ('active', models.BooleanField(default=False, help_text='Activate this questionnaire specification.  Only one questionnaire specification may be active at any given time.')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

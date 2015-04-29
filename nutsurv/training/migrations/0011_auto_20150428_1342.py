# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training', '0010_auto_20150423_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrainingSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameModel(
            old_name='TrainingRoomMember',
            new_name='TrainingSubject',
        ),
        migrations.RemoveField(
            model_name='trainingroom',
            name='creator',
        ),
        migrations.DeleteModel(
            name='TrainingRoom',
        ),
    ]

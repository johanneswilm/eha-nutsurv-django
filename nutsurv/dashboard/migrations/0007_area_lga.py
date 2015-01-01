# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_clustersjson'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_0', models.CharField(max_length=255)),
                ('name_1', models.CharField(max_length=255)),
                ('name_2', models.CharField(max_length=255)),
                ('varname_2', models.CharField(max_length=255)),
                ('mpoly', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LGA',
            fields=[
                ('area_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.Area')),
            ],
            options={
            },
            bases=('dashboard.area',),
        ),
    ]

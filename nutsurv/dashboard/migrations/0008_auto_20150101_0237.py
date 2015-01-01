# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_area_lga'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='mpoly',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(help_text=b'A multi-polygon field defining boundaries of this area', srid=4326),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_0',
            field=models.CharField(help_text=b'The area two levels higher than this one (i.e. the area containing the area which contains this area (e.g. the name of a country))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_1',
            field=models.CharField(help_text=b'The area one level higher than this one (i.e. the area containing this area (e.g. the name of a state))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_2',
            field=models.CharField(help_text=b'The name of this area (e.g. the name of an LGA))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='varname_2',
            field=models.CharField(help_text=b'Alternative name for this area (optional, can be left blank)', max_length=255, blank=True),
        ),
    ]

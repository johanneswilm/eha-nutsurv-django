# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20150310_1503'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clusters',
            fields=[
                ('uniqueactivenameddocument_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dashboard.UniqueActiveNamedDocument')),
                ('json', jsonfield.fields.JSONField(default={}, help_text='Please enter the JSON structure describing all the clusters for the planned survey.', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'The "Clusters" documents',
            },
            bases=('dashboard.uniqueactivenameddocument',),
        ),
        migrations.DeleteModel(
            name='ClustersJSON',
        ),
        migrations.AlterModelOptions(
            name='clustersperstate',
            options={'verbose_name_plural': 'The "Clusters per 1st Admin" documents'},
        ),
        migrations.AlterModelOptions(
            name='lga',
            options={'verbose_name': '2nd Admin'},
        ),
        migrations.AlterModelOptions(
            name='states',
            options={'verbose_name_plural': 'The "1st Admin" documents'},
        ),
        migrations.AlterModelOptions(
            name='stateswithreserveclusters',
            options={'verbose_name_plural': 'The "1st Admin with Reserve Clusters" documents'},
        ),
        migrations.RemoveField(
            model_name='questionnairespecification',
            name='active',
        ),
        migrations.RemoveField(
            model_name='questionnairespecification',
            name='created',
        ),
        migrations.RemoveField(
            model_name='questionnairespecification',
            name='id',
        ),
        migrations.RemoveField(
            model_name='questionnairespecification',
            name='last_modified',
        ),
        migrations.RemoveField(
            model_name='questionnairespecification',
            name='name_or_id',
        ),
        migrations.AddField(
            model_name='questionnairespecification',
            name='uniqueactivedocument_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=False, serialize=False, to='dashboard.UniqueActiveDocument'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='area',
            name='name_1',
            field=models.CharField(help_text=b'The area one level higher than this one (i.e. the area containing this area (e.g. the name of a 1st Admin))', max_length=255),
        ),
        migrations.AlterField(
            model_name='area',
            name='name_2',
            field=models.CharField(help_text=b'The name of this area (e.g. the name of an 2nd Admin))', max_length=255),
        ),
        migrations.AlterField(
            model_name='clustersperstate',
            name='json',
            field=jsonfield.fields.JSONField(default={}, help_text='Please enter the JSON structure defining the number of standard and reserve clusters per 1st Admin.  E.g.: { "states": { "Kano": { "standard": 5, "reserve": 3 }, "Lagos": { "standard": 7, "reserve": 3 } } }', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='clustersperteam',
            name='json',
            field=jsonfield.fields.JSONField(default={}, help_text='Please enter the JSON structure defining the (planned) number of clusters per each team.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='states',
            name='json',
            field=jsonfield.fields.JSONField(default=[], help_text='Please enter the JSON structure defining the 1st Admin area data.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='stateswithreserveclusters',
            name='json',
            field=jsonfield.fields.JSONField(default=[], help_text='Please enter the JSON structure describing the 1st Admin with reserve clusters enabled.', null=True, blank=True),
        ),
    ]

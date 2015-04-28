# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0018_auto_20150421_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='alert_type',
            field=models.CharField(default='haha, who knows', max_length=255, choices=[(b'mapping_check_missing_cluster_id', b'mapping_check_missing_cluster_id'), (b'mapping_check_missing_location', b'mapping_check_missing_location'), (b'mapping_check_unknown_cluster', b'mapping_check_unknown_cluster'), (b'mapping_check_wrong_location', b'mapping_check_wrong_location'), (b'sex_ratio', b'sex_ratio'), (b'child_age_in_months_ratio', b'child_age_in_months_ratio'), (b'child_age_displacement', b'child_age_displacement'), (b'woman_age_14_15_displacement', b'woman_age_14_15_displacement'), (b'woman_age_4549_5054_displacement', b'woman_age_4549_5054_displacement'), (b'digit_preference', b'digit_preference'), (b'data_collection_time', b'data_collection_time'), (b'time_to_complete_single_survey', b'time_to_complete_single_survey'), (b'daily_data_collection_duration', b'daily_data_collection_duration')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alert',
            name='category',
            field=models.CharField(default=b'general', max_length=255, choices=[(b'general', b'general'), (b'map', b'map'), (b'sex', b'sex'), (b'age_distribution', b'age_distribution'), (b'number_distribution', b'number_distribution'), (b'timing', b'timing')]),
            preserve_default=True,
        ),
    ]

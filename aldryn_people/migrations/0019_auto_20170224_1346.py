# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0018_auto_20160802_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='sort_order',
            field=models.IntegerField(default=999999, verbose_name='sort order', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='sort_order',
            field=models.IntegerField(default=999999, verbose_name='sort order', blank=True),
        ),
    ]

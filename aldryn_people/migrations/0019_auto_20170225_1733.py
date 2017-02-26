# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0018_auto_20160802_1852'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ['sort_order'], 'verbose_name': 'Group', 'verbose_name_plural': 'Groups'},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['sort_order'], 'verbose_name': 'Person', 'verbose_name_plural': 'People'},
        ),
        migrations.AddField(
            model_name='group',
            name='sort_order',
            field=models.IntegerField(default=999999, verbose_name='sort order', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='show_in_menu',
            field=models.BooleanField(default=False, verbose_name='show in group menu list'),
        ),
        migrations.AddField(
            model_name='person',
            name='sort_order',
            field=models.IntegerField(default=999999, verbose_name='sort order', blank=True),
        ),
    ]

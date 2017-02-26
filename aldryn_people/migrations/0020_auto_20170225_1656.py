# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0019_auto_20170224_1346'),
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
    ]

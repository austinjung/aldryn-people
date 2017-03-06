# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import aldryn_common.admin_fields.sortedm2m


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0020_auto_20170228_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='peopleplugin',
            name='groups',
            field=aldryn_common.admin_fields.sortedm2m.SortedM2MModelField(help_text='Select and arrange specific groups, or, leave blank to select specific people.', to='aldryn_people.Group', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='parish_account',
            field=models.CharField(default=None, max_length=30, null=True, verbose_name='Parish Account', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='relationship',
            field=models.CharField(default='self', max_length=50, verbose_name='Relationship', choices=[('self', 'Self'), ('spouse', 'Spouse'), ('child', 'Child'), ('other', 'Other')]),
        ),
    ]

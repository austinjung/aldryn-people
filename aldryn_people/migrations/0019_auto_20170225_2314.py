# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


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
            name='show_in_menu',
            field=models.BooleanField(default=True, verbose_name='show in group menu list'),
        ),
        migrations.AddField(
            model_name='group',
            name='sort_order',
            field=models.IntegerField(default=999999, verbose_name='sort order', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='city',
            field=models.CharField(default='', max_length=20, verbose_name='City', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='country',
            field=models.CharField(default='Canada', max_length=20, verbose_name='Country', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='email_confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='person',
            name='latitude',
            field=models.FloatField(null=True, verbose_name='Latitude', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='longitude',
            field=models.FloatField(null=True, verbose_name='Longitude', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='postal',
            field=models.CharField(default='', max_length=7, verbose_name='Postal Code', blank=True, validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z ][0-9 ][a-zA-Z ] [0-9 ][a-zA-Z ][0-9 ]$', message='Ex: V1V 9Y9', code='Invalid Postal Code')]),
        ),
        migrations.AddField(
            model_name='person',
            name='province',
            field=models.CharField(default='BC', max_length=20, verbose_name='Province', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='sort_order',
            field=models.IntegerField(default=999999, verbose_name='sort order', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='street',
            field=models.CharField(default='', max_length=20, verbose_name='Street/Avenue', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='street_number',
            field=models.CharField(default='', max_length=10, verbose_name='Street number', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='unit_number',
            field=models.CharField(default='', max_length=10, verbose_name='Unit number', blank=True),
        ),
    ]

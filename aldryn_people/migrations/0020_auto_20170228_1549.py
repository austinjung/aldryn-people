# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import parler.models
import aldryn_translation_tools.models
import django.contrib.postgres.fields
import djangocms_text_ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('aldryn_people', '0019_auto_20170225_2314'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegionalGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('latitudes', django.contrib.postgres.fields.ArrayField(default=[], size=None, base_field=models.FloatField(), blank=True)),
                ('longitudes', django.contrib.postgres.fields.ArrayField(default=[], size=None, base_field=models.FloatField(), blank=True)),
                ('number_of_sections', models.IntegerField(default=1, verbose_name='number of sections', blank=True)),
            ],
            options={
                'verbose_name': 'Regional Group',
                'verbose_name_plural': 'Regional Groups',
            },
            bases=(aldryn_translation_tools.models.TranslationHelperMixin, aldryn_translation_tools.models.TranslatedAutoSlugifyMixin, parler.models.TranslatableModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RegionalGroupTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language_code', models.CharField(max_length=15, verbose_name='Language', db_index=True)),
                ('name', models.CharField(help_text="Provide this regional group's name.", max_length=255, verbose_name='name')),
                ('description', djangocms_text_ckeditor.fields.HTMLField(verbose_name='description', blank=True)),
                ('slug', models.SlugField(default='', max_length=255, blank=True, help_text='Leave blank to auto-generate a unique slug.', verbose_name='slug')),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='aldryn_people.RegionalGroup', null=True)),
            ],
            options={
                'managed': True,
                'db_table': 'aldryn_people_regionalgroup_translation',
                'db_tablespace': '',
                'default_permissions': (),
                'verbose_name': 'Regional Group Translation',
            },
        ),
        migrations.AddField(
            model_name='person',
            name='regional_section_number',
            field=models.IntegerField(default=None, null=True, verbose_name='Regional section number', blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='regional_group',
            field=models.ForeignKey(related_name='people', default=None, blank=True, to='aldryn_people.RegionalGroup', help_text='Choose the regional groups for this person.', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='regionalgrouptranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]

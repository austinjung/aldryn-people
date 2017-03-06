# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from collections import defaultdict, OrderedDict

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from aldryn_people import models, DEFAULT_APP_NAMESPACE
from .utils import get_valid_languages


NAMESPACE_ERROR = _(
    "Seems that there is no valid application hook for aldryn-people."
    "Links can't be rendered without an app hook."
)


class PeoplePlugin(CMSPluginBase):

    TEMPLATE_NAME = 'aldryn_people/plugins/%s/people_list.html'
    module = 'People'
    render_template = TEMPLATE_NAME % models.PeoplePlugin.STYLE_CHOICES[0][0]
    name = _('People list')
    model = models.PeoplePlugin

    fieldsets = (
        (None, {
            'fields': (
                'style',
            ),
        }),
        (_('Group Filter'), {
            'description': _('Select and arrange specific groups, or leave '
                             'blank to not use group filters at all.'),
            'fields': (
                'groups',
            )
        }),
        (_('People'), {
            'description': _('Select and arrange specific people, or leave '
                             'blank to use all.'),
            'fields': (
                'people',
            )
        }),
        (_('Options'), {
            'fields': (
                ('group_by_group', 'show_ungrouped', ),
                'show_links',
                'show_vcard',
            )
        })
    )

    def group_people(self, people, selected_groups=None):
        groups = OrderedDict()
        for group in selected_groups:
            groups[group] = []

        for person in people:
            if selected_groups is None:
                for group in person.groups.all():
                    groups[group].append(person)
            else:
                selected_group_ids = [group.id for group in selected_groups]
                for group in person.groups.filter(id__in=selected_group_ids):
                    groups[group].append(person)

        return groups

    def render(self, context, instance, placeholder):
        selected_groups = instance.get_selected_groups()
        if selected_groups.count() == 0:
            people = instance.get_selected_people()
            if not people:
                people = models.Person.objects.all()
        else:
            people = models.Person.objects.filter(groups__in=selected_groups)
        valid_languages = get_valid_languages(
            DEFAULT_APP_NAMESPACE, instance.language, context['request'])
        people = people.translated(*valid_languages)
        if not valid_languages:
            context['namespace_error'] = NAMESPACE_ERROR
        self.render_template = self.TEMPLATE_NAME % instance.style

        context['instance'] = instance
        context['people'] = people

        if instance.group_by_group and selected_groups.count() > 0:
            context['people_groups'] = self.group_people(people, selected_groups=selected_groups)
            if instance.show_ungrouped:
                groupless = people.filter(groups__isnull=True)
            else:
                groupless = people.none()
            context['groupless_people'] = groupless
        else:
            context['people_groups'] = []
            context['groupless_people'] = people.none()
        return context

plugin_pool.register_plugin(PeoplePlugin)

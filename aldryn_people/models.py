# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import six
from aldryn_people.vcard import Vcard

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
import warnings

from reversion.revisions import (
    default_revision_manager, RegistrationError
)

from distutils.version import LooseVersion
from django import get_version
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
try:
    # Python>=2.7
    from importlib import import_module
except ImportError:
    # Python==2.6
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from django.utils.importlib import import_module

from django.utils.translation import ugettext_lazy as _, override, force_text
from six import text_type

from aldryn_common.admin_fields.sortedm2m import SortedM2MModelField
from aldryn_translation_tools.models import (
    TranslatedAutoSlugifyMixin,
    TranslationHelperMixin,
)
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language, get_default_language
from djangocms_text_ckeditor.fields import HTMLField
from filer.fields.image import FilerImageField
from parler.models import TranslatableModel, TranslatedFields
from aldryn_reversion.core import version_controlled_content
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField


from .utils import get_additional_styles, get_geographic_coordinates

# NOTE: We use LooseVersion and not StrictVersion because sometimes Aldryn uses
# patched build with version numbers of the form X.Y.Z.postN.
loose_version = LooseVersion(get_version())

if loose_version < LooseVersion('1.7.0'):
    LTE_DJANGO_1_6 = True
    # Prior to 1.7 it is pretty straight forward
    user_model = get_user_model()
    if user_model not in default_revision_manager.get_registered_models():
        default_revision_manager.register(user_model)
else:
    # otherwise it is a pain, but thanks to solution of getting model from
    # https://github.com/django-oscar/django-oscar/commit/c479a1
    # we can do almost the same thing from the different side.
    from django.apps import apps
    from django.apps.config import MODELS_MODULE_NAME
    from django.core.exceptions import AppRegistryNotReady

    LTE_DJANGO_1_6 = False

    def get_model(app_label, model_name):
        """
        Fetches a Django model using the app registry.
        This doesn't require that an app with the given app label exists,
        which makes it safe to call when the registry is being populated.
        All other methods to access models might raise an exception about the
        registry not being ready yet.
        Raises LookupError if model isn't found.
        """
        try:
            return apps.get_model(app_label, model_name)
        except AppRegistryNotReady:
            if apps.apps_ready and not apps.models_ready:
                # If this function is called while `apps.populate()` is
                # loading models, ensure that the module that defines the
                # target model has been imported and try looking the model up
                # in the app registry. This effectively emulates
                # `from path.to.app.models import Model` where we use
                # `Model = get_model('app', 'Model')` instead.
                app_config = apps.get_app_config(app_label)
                # `app_config.import_models()` cannot be used here because it
                # would interfere with `apps.populate()`.
                import_module('%s.%s' % (app_config.name, MODELS_MODULE_NAME))
                # In order to account for case-insensitivity of model_name,
                # look up the model through a private API of the app registry.
                return apps.get_registered_model(app_label, model_name)
            else:
                # This must be a different case (e.g. the model really doesn't
                # exist). We just re-raise the exception.
                raise

    # now get the real user model
    user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
    model_app_name, model_model = user_model.split('.')
    user_model_object = get_model(model_app_name, model_model)
    # and try to register, if we have a registration error - that means that
    # it has been registered already
    try:
        default_revision_manager.register(user_model_object)
    except RegistrationError:
        pass


@version_controlled_content
@python_2_unicode_compatible
class Group(TranslationHelperMixin, TranslatedAutoSlugifyMixin,
            TranslatableModel):
    slug_source_field_name = 'name'
    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255,
                              help_text=_("Provide this group's name.")),
        description=HTMLField(_('description'), blank=True),
        slug=models.SlugField(_('slug'), max_length=255, default='',
            blank=True,
            help_text=_("Leave blank to auto-generate a unique slug.")),
    )
    address = models.TextField(
        verbose_name=_('address'), blank=True)
    postal_code = models.CharField(
        verbose_name=_('postal code'), max_length=20, blank=True)
    city = models.CharField(
        verbose_name=_('city'), max_length=255, blank=True)
    phone = models.CharField(
        verbose_name=_('phone'), null=True, blank=True, max_length=100)
    fax = models.CharField(
        verbose_name=_('fax'), null=True, blank=True, max_length=100)
    email = models.EmailField(
        verbose_name=_('email'), blank=True, default='')
    website = models.URLField(
        verbose_name=_('website'), null=True, blank=True)
    sort_order = models.IntegerField(
        verbose_name=_('sort order'), blank=True, default=999999)
    show_in_menu = models.BooleanField(
        verbose_name=_('show in group menu list'), blank=True, default=True)

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def __str__(self):
        return self.safe_translation_getter(
            'name', default=_('Group: {0}').format(self.pk))

    def get_absolute_url(self, language=None):
        if not language:
            language = get_current_language() or get_default_language()
        slug, language = self.known_translation_getter(
            'slug', None, language_code=language)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            return reverse('aldryn_people:group-detail', kwargs=kwargs)


@version_controlled_content
@python_2_unicode_compatible
class RegionalGroup(TranslationHelperMixin, TranslatedAutoSlugifyMixin,
            TranslatableModel):
    slug_source_field_name = 'name'
    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255,
                              help_text=_("Provide this regional group's name.")),
        description=HTMLField(_('description'), blank=True),
        slug=models.SlugField(_('slug'), max_length=255, default='',
            blank=True,
            help_text=_("Leave blank to auto-generate a unique slug.")),
    )
    latitudes = ArrayField(models.FloatField(), default=[], blank=True)
    longitudes = ArrayField(models.FloatField(), default=[], blank=True)
    number_of_sections = models.IntegerField(
        verbose_name=_('number of sections'), blank=True, default=1)

    class Meta:
        verbose_name = _('Regional Group')
        verbose_name_plural = _('Regional Groups')

    def __str__(self):
        return self.safe_translation_getter(
            'name', default=_('Group: {0}').format(self.pk))

    def get_absolute_url(self, language=None):
        if not language:
            language = get_current_language() or get_default_language()
        slug, language = self.known_translation_getter(
            'slug', None, language_code=language)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            return reverse('aldryn_people:group-detail', kwargs=kwargs)

    @property
    def polygons(self):
        return zip(self.latitudes, self.longitudes)


@version_controlled_content(follow=['groups', 'user'])
@python_2_unicode_compatible
class Person(TranslationHelperMixin, TranslatedAutoSlugifyMixin,
             TranslatableModel):
    slug_source_field_name = 'name'

    translations = TranslatedFields(
        name=models.CharField(_('name'), max_length=255, blank=False,
            default='', help_text=_("Provide this person's name.")),
        slug=models.SlugField(_('unique slug'), max_length=255, blank=True,
            default='',
            help_text=_("Leave blank to auto-generate a unique slug.")),
        function=models.CharField(_('role'),
            max_length=255, blank=True, default=''),
        description=HTMLField(_('description'),
            blank=True, default='')
    )
    phone = models.CharField(
        verbose_name=_('phone'), null=True, blank=True, max_length=100)
    mobile = models.CharField(
        verbose_name=_('mobile'), null=True, blank=True, max_length=100)
    fax = models.CharField(
        verbose_name=_('fax'), null=True, blank=True, max_length=100)
    email = models.EmailField(
        verbose_name=_("email"), blank=True, default='')
    website = models.URLField(
        verbose_name=_('website'), null=True, blank=True)
    groups = SortedM2MModelField(
        'aldryn_people.Group', default=None, blank=True, related_name='people',
        help_text=_('Choose and order the groups for this person, the first '
                    'will be the "primary group".'))
    regional_group = models.ForeignKey(
        'aldryn_people.RegionalGroup', default=None, blank=True, null=True, related_name='people',
        help_text=_('Choose the regional groups for this person.'))
    regional_section_number = models.IntegerField(
        verbose_name=_('Regional section number'), blank=True, default=None, null=True)
    visual = FilerImageField(
        null=True, blank=True, default=None, on_delete=models.SET_NULL)
    vcard_enabled = models.BooleanField(
        verbose_name=_('enable vCard download'), default=True)
    user = models.OneToOneField(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        null=True, blank=True, related_name='persons')
    sort_order = models.IntegerField(
        verbose_name=_('sort order'), blank=True, default=999999)
    unit_number = models.CharField(max_length=10, blank=True, default='', verbose_name=_('Unit number'))
    street_number = models.CharField(max_length=10, blank=True, default='', verbose_name=_('Street number'))
    street = models.CharField(max_length=20, blank=True, default='', verbose_name=_('Street/Avenue'))
    city = models.CharField(max_length=20, blank=True, default='', verbose_name=_('City'))
    province = models.CharField(max_length=20, blank=True, default='BC', verbose_name=_('Province'))
    postal = models.CharField(max_length=7, blank=True, default='', verbose_name=_('Postal Code'),
                              validators=[
                                  RegexValidator(
                                      regex='^[a-zA-Z ][0-9 ][a-zA-Z ] [0-9 ][a-zA-Z ][0-9 ]$',
                                      message='Ex: V1V 9Y9',
                                      code=_('Invalid Postal Code')
                                  ),
                              ]
             )
    country = models.CharField(max_length=20, blank=True, default='Canada', verbose_name='Country')
    latitude = models.FloatField(null=True, blank=True, verbose_name='Latitude')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Longitude')
    email_confirmed = models.BooleanField(default=False)

    parish_account = models.CharField(max_length=30, blank=True, null=True, default=None, verbose_name=_('Parish Account'))
    RELATIONSHIP_CHOICES = [
        ('self', _('Self')),
        ('spouse', _('Spouse')),
        ('child', _('Child')),
        ('other', _('Other'))
    ]
    relationship = models.CharField(
        _('Relationship'), choices=RELATIONSHIP_CHOICES,
        default=RELATIONSHIP_CHOICES[0][0], max_length=50)

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('People')

    def __str__(self):
        pkstr = str(self.pk)

        if six.PY2:
            pkstr = six.u(pkstr)
        name = self.safe_translation_getter(
            'name',
            default='',
            any_language=True
        ).strip()
        return name if len(name) > 0 else pkstr

    @property
    def primary_group(self):
        """Simply returns the first in `groups`, if any, else None."""
        return self.groups.first()

    @property
    def comment(self):
        return self.safe_translation_getter('description', '')

    @property
    def address(self):
        address = ''
        if self.unit_number not in ['', None]:
            address += '#%s, ' % self.unit_number
        if self.street_number not in ['', None]:
            address += '%s ' % self.street_number
        if self.street not in ['', None]:
            address += '%s, ' % self.street
        if self.city not in ['', None]:
            address += '%s, ' % self.city
        address += '%s %s, %s' % (self.province, self.postal, self.country)
        return address

    def clean(self):
        geo_location = get_geographic_coordinates(self.get_address_for_geo_location())
        self.longitude = geo_location['lng']
        self.latitude = geo_location['lat']
        if self.regional_section_number and self.regional_group:
            if self.regional_section_number > self.regional_group.number_of_sections:
                self.regional_section_number = None
        else:
            self.regional_section_number = None

    def get_address_for_geo_location(self):
        address = ''
        if self.street_number not in ['', None]:
            address += '%s ' % self.street_number
        else:
            return None
        if self.street not in ['', None]:
            address += '%s, ' % self.street
        else:
            return None
        if self.city not in ['', None]:
            address += '%s, ' % self.city
        else:
            return None
        address += '%s %s, %s' % (self.province, self.postal, self.country)
        return address

    def get_absolute_url(self, language=None):
        if not language:
            language = get_current_language()
        slug, language = self.known_translation_getter(
            'slug', None, language_code=language)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            # do not fail with 500 error so that if detail view can't be
            # resolved we still can use plugins.
            try:
                url = reverse('aldryn_people:person-detail', kwargs=kwargs)
            except NoReverseMatch:
                url = ''
        return url

    def get_vcard_url(self, language=None):
        if not language:
            language = get_current_language()
        slug = self.safe_translation_getter(
            'slug', None, language_code=language, any_language=False)
        if slug:
            kwargs = {'slug': slug}
        else:
            kwargs = {'pk': self.pk}
        with override(language):
            return reverse('aldryn_people:download_vcard', kwargs=kwargs)

    def get_vcard(self, request=None):
        vcard = Vcard()
        person_translation = self.translations.model.objects.get(master_id=self.id, language_code='en')
        function = person_translation.function

        safe_name = person_translation.name
        vcard.add_line('FN', safe_name)
        vcard.add_line('N', [None, safe_name, None, None, None])

        if self.visual:
            ext = self.visual.extension.upper()
            try:
                with open(self.visual.path, 'rb') as f:
                    data = force_text(base64.b64encode(f.read()))
                    vcard.add_line('PHOTO', data, TYPE=ext, ENCODING='b')
            except IOError:
                if request:
                    url = urlparse.urljoin(request.build_absolute_uri(),
                                           self.visual.url),
                    vcard.add_line('PHOTO', url, TYPE=ext)

        if self.email:
            vcard.add_line('EMAIL', self.email)

        if function:
            vcard.add_line('TITLE', function)

        if self.phone:
            vcard.add_line('TEL', self.phone, TYPE='WORK')
        if self.mobile:
            vcard.add_line('TEL', self.mobile, TYPE='CELL')

        if self.fax:
            vcard.add_line('TEL', self.fax, TYPE='FAX')
        if self.website:
            vcard.add_line('URL', self.website)

        # if self.primary_group:
        #     group_name = self.primary_group.safe_translation_getter(
        #         'name', default="Group: {0}".format(self.primary_group.pk))
        #     if group_name:
        #         vcard.add_line('ORG', group_name)
        #     if (self.primary_group.address or self.primary_group.city or
        #             self.primary_group.postal_code):
        #         vcard.add_line('ADR', (
        #             None, None,
        #             self.primary_group.address,
        #             self.primary_group.city,
        #             None,
        #             self.primary_group.postal_code,
        #             None,
        #         ), TYPE='WORK')
        #
        #     if self.primary_group.phone:
        #         vcard.add_line('TEL', self.primary_group.phone, TYPE='WORK')
        #     if self.primary_group.fax:
        #         vcard.add_line('TEL', self.primary_group.fax, TYPE='FAX')
        #     if self.primary_group.website:
        #         vcard.add_line('URL', self.primary_group.website)

        return str(vcard)


@python_2_unicode_compatible
class BasePeoplePlugin(CMSPlugin):

    STYLE_CHOICES = [
        ('standard', _('Standard')),
        ('feature', _('Feature'))
    ] + get_additional_styles()

    style = models.CharField(
        _('Style'), choices=STYLE_CHOICES,
        default=STYLE_CHOICES[0][0], max_length=50)

    people = SortedM2MModelField(
        Person, blank=True,
        help_text=_('Select and arrange specific people, or, leave blank to '
                    'select all.')
    )

    groups = SortedM2MModelField(
        Group, blank=True,
        help_text=_('Select and arrange specific groups, or, leave blank to '
                    'select specific people.')
    )

    # Add an app namespace to related_name to avoid field name clashes
    # with any other plugins that have a field with the same name as the
    # lowercase of the class name of this model.
    # https://github.com/divio/django-cms/issues/5030
    if LTE_DJANGO_1_6:
        # related_name='%(app_label)s_%(class)s' does not work on  Django 1.6
        cmsplugin_ptr = models.OneToOneField(
            CMSPlugin,
            related_name='+',
            parent_link=True,
        )
    else:
        cmsplugin_ptr = models.OneToOneField(
            CMSPlugin,
            related_name='%(app_label)s_%(class)s',
            parent_link=True,
        )

    class Meta:
        abstract = True

    def copy_relations(self, oldinstance):
        self.people = oldinstance.people.all()
        self.groups = oldinstance.groups.all()

    def get_selected_groups(self):
        return self.groups.select_related()

    def get_selected_people(self):
        return self.people.select_related('visual')

    def __str__(self):
        return text_type(self.pk)


class PeoplePlugin(BasePeoplePlugin):

    group_by_group = models.BooleanField(
        verbose_name=_('group by group'),
        default=True,
        help_text=_('Group people by their group.')
    )
    show_ungrouped = models.BooleanField(
        verbose_name=_('show ungrouped'),
        default=False,
        help_text=_('When using "group by group", show ungrouped people too.')
    )
    show_links = models.BooleanField(
        verbose_name=_('Show links to Detail Page'), default=False)
    show_vcard = models.BooleanField(
        verbose_name=_('Show links to download vCard'), default=False)

    class Meta:
        abstract = False

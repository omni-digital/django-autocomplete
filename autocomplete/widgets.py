from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.utils.safestring import mark_safe
from django import forms

from autocomplete import add_searchable_fields, AUTOCOMPLETE_URL_NAME

class AutocompleteSelectMultiple(forms.SelectMultiple):
    """
    To use this widget, you need jQuery, jQuery UI and jQuery UI theme stylesheet
    Add
    """
    class Media:
        css = {
            'all': (
                settings.STATIC_URL+'autocomplete/styles/jquery.autocompleteSelectMultiple.css',
            ),
        }
        js = (
            settings.STATIC_URL+'autocomplete/scripts/jquery.autocompleteSelectMultiple.js',
        )

    def __init__(self, model, search_fields=None, url_name=AUTOCOMPLETE_URL_NAME, attrs=None):
        if hasattr(model, 'to'):
            # This is a relation manager 
            self.model = model.to
        else:
            self.model = model

        self.search_fields = search_fields
        self.url_name = url_name

        if (search_fields):
            # Allow these fields (for this model) to be searched 
            add_searchable_fields(self.model, self.search_fields)

        super(AutocompleteSelectMultiple, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        self.choices = value and [(o.pk, unicode(o)) for o in self.model.objects.filter(pk__in=value)] or []

        rendered = super(AutocompleteSelectMultiple, self).render(name,value, attrs)

        return rendered + mark_safe(u'''
            <script>
                $(document).ready(function() {
                    $('.autocompleteSelectMultiple').autocompleteSelectMultiple({
                        'url' : '%(url)s',
                        'search_fields' : '%(search_fields)s',
                        'content_type' : %(content_type)s
                    });
                });
            </script>
            <div class="autocompleteSelectMultiple">
                <ul>
                    <li><input id="search_input" class="search_input" name="search_input" type="text"></li>
                </ul>
            </div>
        ''' % {
            'url': reverse(self.url_name),
            'search_fields' :  self.search_fields and ','.join(self.search_fields) or "",
            'content_type' : ContentType.objects.get_for_model(self.model).pk,
        })

class AutocompleteTag(forms.TextInput):
    """
    To use this widget, you need jQuery, jQuery UI and jQuery UI theme stylesheet
    Add
    """
    class Media:
        css = {
           'all': (
               settings.STATIC_URL+'autocomplete/styles/jquery.autocompleteTag.css',
           ),
        }
        js = (
            settings.STATIC_URL+'autocomplete/scripts/jquery.autocompleteTag.js',
        )

    def __init__(self, model=None, search_fields=None, url_name=AUTOCOMPLETE_URL_NAME, attrs=None):

        if model is None:
            if hasattr(settings, 'AUTOCOMPLETE_TAG_MODEL'):
                model = apps.get_model(*settings.AUTOCOMPLETE_TAG_MODEL.split('.', 2))
            else:
                raise ImproperlyConfigured("AUTOCOMPLETE_TAG_MODEL setting not set. Set it to the name of the tag model to autocomplete.")

        self.model = model
        self.search_fields = search_fields
        self.url_name = url_name

        if (search_fields):
            # Allow these fields (for this model) to be searched 
            add_searchable_fields(self.model, self.search_fields)

        super(AutocompleteTag, self).__init__(attrs)


    def render(self, name, value, attrs=None):

        if value is not None and not isinstance(value, basestring):
            value = ", ".join([str(getattr(o, 'tag', o)) for o in value])

        rendered = super(AutocompleteTag, self).render(name, value, attrs)

        return rendered + mark_safe(u'''
            <script>
                $(document).ready(function() {
                    $('#%(id)s').autocompleteTag({
                                    'url' : '%(url)s',
                                    'search_fields' : '%(search_fields)s',
                                    'content_type' : %(content_type)s
                                   });
                });
            </script>
        ''' % {
            'id': attrs['id'],
            'url': reverse(self.url_name),
            'search_fields' :  self.search_fields and ','.join(self.search_fields) or "",
            'content_type' : ContentType.objects.get_for_model(self.model).pk,
        })


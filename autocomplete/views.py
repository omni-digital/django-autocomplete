import json
import operator

from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured


from autocomplete import get_searchable_fields

"""
# Set the models autocomplete will search.
AUTOCOMPLETE_MODELS = {
   'profiles.Profile': ['email', 'first_name', 'last_name',],
}
"""


def get_field_lookup_pair(field_name):
    # use different lookup methods depending on the notation
    if field_name.startswith('^'):
        return field_name[1:], 'istartswith'
    elif field_name.startswith('='):
        return field_name[1:], 'iexact'
    elif field_name.startswith('@'):
        return field_name[1:], 'search'
    else:
        return field_name, 'icontains'


def construct_search(field_name):
    # use different lookup methods depending on the notation
    return "%s__%s" % get_field_lookup_pair(field_name)


def search(request):
    """
    Searches in the fields of the given model and returns the
    result as a simple json list of objects to be used by the jQuery
    autocomplete plugin.

    Usage:
        In settings set:
        AUTOCOMPLETE_MODELS = {
            'profiles.Profile': ['email', 'first_name', 'last_name',],
        }

        /autocomplete/?ct=47&q=a

            >>>

        [
            {"value": 2, "label": "Jim Morris"},
            {"value": 1, "label": "Ad Min"}
        ]
    """

    content_type = request.GET.get('ct', None)
    if content_type is not None:
        model = ContentType.objects.get(pk=content_type).model_class()
    else:
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        model = models.get_model(app_label, model_name)

    if not model:
        return HttpResponseNotFound()

    allowed_fields = get_searchable_fields(model)
    if not allowed_fields:
        raise ImproperlyConfigured('The model %s.%s being autocompleted it does not have allowed fields. '
                                   'If you are using the autocomplete search whithout an autocomplete widget then add the '
                                   'app_label.model and searchable fields to the AUTOCOMPLETE_MODELS dictionary in your setting.' % \
                                   (model._meta.app_label, model._meta.module_name))

    search_fields = request.GET.get('sf', None)

    if search_fields is None:
        search_fields = allowed_fields
    else:
        # Limit to search fields
        search_fields = search_fields.split(',')
        search_fields = filter(lambda f: get_field_lookup_pair(f)[0] in map(lambda f: get_field_lookup_pair(f)[0], allowed_fields), search_fields)

    query = request.GET.get('term', None)

    if search_fields and query:
        qs = model._default_manager.all()
        for bit in query.split():
            or_queries = [models.Q(**{construct_search(smart_str(field_name)): smart_str(bit)})
                          for field_name in search_fields]
            other_qs = QuerySet(model)
            other_qs.dup_select_related(qs)
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            qs = qs & other_qs

        data = [{'label': o.__unicode__(), 'value': o.pk} for o in qs]

        return HttpResponse(json.dumps(data), mimetype='application/javascript')

    return HttpResponseNotFound()

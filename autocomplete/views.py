import operator
import warnings
from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.contenttypes.models import ContentType
from django.utils import simplejson
from django.core.exceptions import ImproperlyConfigured
from django.template.defaultfilters import capfirst


AUTOCOMPLETE_MODELS = getattr(settings, 'AUTOCOMPLETE_MODELS', None)

if AUTOCOMPLETE_MODELS is None:
    raise ImproperlyConfigured("""Set the AUTOCOMPLETE_MODELS setting to control which models can be searched.""")

"""
#Allow autocomplete to search any models
AUTOCOMPLETE_MODELS = True
#Limit the models autocomplete will search but do not limit the fields that can be searched. 
AUTOCOMPLETE_MODELS = {
   'profiles.Profile': True,
}
#Limit the models autocomplete will search. 
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
    return  "%s__%s" % get_field_lookup_pair(field_name)


def search(request):
    """
    Searches in the fields of the given model and returns the 
    result as a simple json list of objects to be used by the jQuery autocomplete plugin.

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

    if AUTOCOMPLETE_MODELS == True:
        allowed_fields = True
    else:
        try :
            allowed_fields = AUTOCOMPLETE_MODELS['%s.%s' % (model._meta.app_label, model._meta.module_name)]
        except KeyError:
            try :
                allowed_fields = AUTOCOMPLETE_MODELS['%s.%s' % (model._meta.app_label, capfirst(model._meta.module_name))]
            except KeyError:
                warnings.warn("""The model %s.%s is not in you list of allowed AUTOCOMPLETE_MODELS""" % (model._meta.app_label, model._meta.module_name))
                return HttpResponseNotFound()


    search_fields = request.GET.get('sf', None)

    if search_fields is None:
        if isinstance(allowed_fields, (list, tuple)):
            # No search_fields use the allowed_fields list
            search_fields = allowed_fields
        else:
            # Nothing to search
            return HttpResponseNotFound()
    else:
        search_fields = search_fields.split(',')
        if isinstance(allowed_fields, (list, tuple)) or getattr(allowed_fields, '__iter__', False):
            # Limit to search fields
            search_fields = filter(lambda f: get_field_lookup_pair(f)[0] in allowed_fields, search_fields)

    query = request.GET.get('q', None)

    if model and search_fields and query:
        qs = model._default_manager.all()
        for bit in query.split():
            or_queries = [models.Q(**{construct_search(smart_str(field_name)): smart_str(bit)})
                          for field_name in search_fields]
            other_qs = QuerySet(model)
            other_qs.dup_select_related(qs)
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            qs = qs & other_qs

        data = [{'label': o.__unicode__(), 'value': o.pk} for o in qs]
        return HttpResponse(simplejson.dumps(data), mimetype='application/javascript')

    return HttpResponseNotFound()




import operator
from django.db import models
from django.http import HttpResponse, HttpResponseNotFound
from django.db.models.query import QuerySet
from django.utils.encoding import smart_str

from django.contrib.contenttypes.models import ContentType

from django.utils import simplejson

def search(request):
    """
    Searches in the fields of the given model and returns the 
    result as a simple json list of objects to be used by the jQuery autocomplete plugin.

    Usage:

        /autocomplete/?ct=47&sf=email,first_name,last_name&q=a

            >>>

        [
            {"value": 2, "label": "Jim Morris"}, 
            {"value": 1, "label": "Ad Min"}
        ]
    """
    query = request.GET.get('q', None)
    search_fields = request.GET.get('sf', None)

    content_type = request.GET.get('ct', None)
    if content_type is not None:
        model = ContentType.objects.get(pk=content_type).model_class()
    else:
        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        model = models.get_model(app_label, model_name)

    if model and search_fields and query:
        def construct_search(field_name):
            # use different lookup methods depending on the notation
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        qs = model._default_manager.all()
        for bit in query.split():
            or_queries = [models.Q(**{construct_search(
                smart_str(field_name)): smart_str(bit)})
                    for field_name in search_fields.split(',')]
            other_qs = QuerySet(model)
            other_qs.dup_select_related(qs)
            other_qs = other_qs.filter(reduce(operator.or_, or_queries))
            qs = qs & other_qs

        data = [{'label': o.__unicode__(), 'value': o.pk} for o in qs]
        return HttpResponse(simplejson.dumps(data), mimetype='application/javascript')

    return HttpResponseNotFound()




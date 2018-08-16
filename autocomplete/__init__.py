import os
if 'DJANGO_SETTINGS_MODULE' in os.environ:
    from django.conf import settings
    from django.template.defaultfilters import capfirst

    AUTOCOMPLETE_URL_NAME = getattr(settings, 'AUTOCOMPLETE_URL_NAME', 'autocomplete_search')
    AUTOCOMPLETE_MODELS = getattr(settings, 'AUTOCOMPLETE_MODELS', {})

    def get_searchable_fields(model):
        try :
            return AUTOCOMPLETE_MODELS['%s.%s' % (model._meta.app_label, model._meta.model_name)]
        except KeyError:
            try :
                return AUTOCOMPLETE_MODELS['%s.%s' % (model._meta.app_label, capfirst(model._meta.model_name))]
            except KeyError:
                return []

    def set_searchable_fields(model, fields):
        model_label = '%s.%s' % (model._meta.app_label, model._meta.model_name)
        AUTOCOMPLETE_MODELS[model_label] = fields

    def add_searchable_fields(model, new_fields):
        fields = get_searchable_fields(model)

        for f in new_fields:
            if not f in fields:
                fields.append(f)

        set_searchable_fields(model, fields)

__version__ = (2, 0, 3)
def get_version():
    return '.'.join(map(str, __version__))

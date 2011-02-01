from django.conf.urls.defaults import *

urlpatterns = patterns(
    'autocomplete.views',
    url(r'^$', 'search', name='autocomplete_search'),
)

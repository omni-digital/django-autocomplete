from django.conf.urls import patterns, url

urlpatterns = patterns(
    'autocomplete.views',
    url(r'^$', 'search', name='autocomplete_search'),
)

from django.conf.urls import patterns, url
from autocomplete.views import search

urlpatterns = [
    url(r'^$', search, name='autocomplete_search'),
]

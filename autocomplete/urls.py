from django.conf.urls import url

from autocomplete.views import search


urlpatterns = [
    url(r'^$', search, name='autocomplete_search'),
]

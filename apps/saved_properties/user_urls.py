from django.urls import path

from apps.saved_properties.views import SavedPropertiesListView


urlpatterns = [
    path(
        'saved-properties/',
        SavedPropertiesListView.as_view(),
        name='saved-properties',
    ),
]

from django.urls import path

from apps.saved_properties.views import (
    SavePropertyView,
    SavedPropertiesListView,
    SharePropertyView,
)

urlpatterns = [
    path(
        '<int:pk>/save/',
        SavePropertyView.as_view(),
        name='save-property',
    ),
    path(
        '<int:pk>/share/',
        SharePropertyView.as_view(),
        name='share-property',
    ),
]

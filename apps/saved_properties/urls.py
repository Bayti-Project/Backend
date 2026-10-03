
from django.urls import path

from apps.saved_properties.views import (
    SavePropertyView,
    SavedPropertiesListView,
)

urlpatterns = [
    path(
        '<int:pk>/save/',
        SavePropertyView.as_view(),
        name='save-property',
    ),
]
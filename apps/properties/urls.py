from django.urls import path
from apps.properties.views import PropertyCreateView, PropertyEditView

app_name = 'properties'

urlpatterns = [
   path('', PropertyCreateView.as_view(), name='property-create'),
   path('<int:pk>/', PropertyEditView.as_view(), name='property-edit'),
]
from django.urls import path
from apps.properties.views import PropertyCreateView
from apps.properties.read_views import PropertyDetailView
from apps.properties.lifecycle_views import PropertyStatusView
from apps.properties.search_views import PropertySearchView

app_name = 'properties'

urlpatterns = [
   path('search/', PropertySearchView.as_view(), name='property-search'),
   path('', PropertyCreateView.as_view(), name='property-create'),
   path('<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
   path('<int:pk>/status/', PropertyStatusView.as_view(), name='property-status'),
]
from django.urls import path
from apps.properties.views import PropertyCreateView
from apps.properties.read_views import PropertyDetailView
from apps.properties.lifecycle_views import (
    PropertyStatusView,
    PropertyContactSettingsView,
)
from apps.properties.search_views import PropertySearchView, TenantHomeView
from apps.properties.my_properties_views import MyPropertiesView
from apps.properties.contact_views import PropertyContactView

app_name = 'properties'

urlpatterns = [
   path('search/', PropertySearchView.as_view(), name='property-search'),
   path('mine/', MyPropertiesView.as_view(), name='property-mine'),
   path('', PropertyCreateView.as_view(), name='property-create'),
   path('<int:pk>/', PropertyDetailView.as_view(), name='property-detail'),
   path('<int:pk>/status/', PropertyStatusView.as_view(), name='property-status'),
   path('<int:pk>/contact-settings/',PropertyContactSettingsView.as_view(), name='property-contact-settings',),
   path('<int:pk>/contact/', PropertyContactView.as_view(), name='property-contact'),
   path('home/', TenantHomeView.as_view(), name='tenant-home'),
]
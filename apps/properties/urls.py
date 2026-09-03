from django.urls import path
from apps.properties.views import PropertyCreateView

app_name = 'properties'

urlpatterns = [
   path('', PropertyCreateView.as_view(), name='property-create'),
    # Edit Property -> سيُضاف في US-07
]
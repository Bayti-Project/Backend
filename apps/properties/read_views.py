from rest_framework import generics, permissions

from apps.properties.models import Property
from apps.properties.serializers.read_serializers import PropertyDetailSerializer
from apps.properties.views import PropertyEditView
from apps.properties.lifecycle_views import PropertyDeleteView


class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyDetailSerializer
    permission_classes = [permissions.AllowAny]

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return super().dispatch(request, *args, **kwargs)

        if request.method == 'DELETE':
            return PropertyDeleteView.as_view()(request, *args, **kwargs)

        return PropertyEditView.as_view()(request, *args, **kwargs)
from rest_framework import generics, permissions
from apps.properties.models import Property
from apps.properties.permissions import IsPropertyOwner
from apps.properties.serializers.status_serializers import PropertyStatusSerializer


class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPropertyOwner]


class PropertyStatusView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsPropertyOwner]
    http_method_names = ['patch']
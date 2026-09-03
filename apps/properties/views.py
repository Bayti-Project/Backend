from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser

from apps.properties.models import Property
from apps.properties.permissions import IsPropertyOwner
from apps.properties.serializers.write_serializers import ( PropertyCreateSerializer,
    PropertyEditSerializer,
)



class PropertyCreateView(generics.CreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class PropertyEditView(generics.RetrieveUpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyEditSerializer
    permission_classes = [permissions.IsAuthenticated, IsPropertyOwner]
    parser_classes = [MultiPartParser, FormParser]

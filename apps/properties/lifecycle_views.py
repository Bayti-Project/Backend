from rest_framework import generics, permissions, status
from rest_framework.response import Response
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


class PropertyContactSettingsView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPropertyOwner]
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        property_obj = self.get_object()

        interest_enabled = request.data.get('interest_enabled')

        if not isinstance(interest_enabled, bool):
            return Response(
                {
                    'message': 'interest_enabled must be true or false.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        property_obj.interest_enabled = interest_enabled
        property_obj.save(update_fields=['interest_enabled'])

        return Response(
            {
                'message': 'Contact settings updated successfully.',
                'interest_enabled': property_obj.interest_enabled
            },
            status=status.HTTP_200_OK
        )
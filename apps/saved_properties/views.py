from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated
from django.shortcuts import get_object_or_404
from apps.properties.models import Property
from apps.saved_properties.models import SavedProperty
from apps.saved_properties.serializers import SavedPropertySerializer

class ArabicIsAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
        )


class SavePropertyView(APIView):
    permission_classes = [ArabicIsAuthenticated]

    def initial(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated('الرجاء تسجيل الدخول')

        super().initial(request, *args, **kwargs)

    def post(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)

        if SavedProperty.objects.filter(
            user=request.user,
            property=property_obj
        ).exists():
            return Response(
                {'message': 'Property is already saved.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        SavedProperty.objects.create(
            user=request.user,
            property=property_obj
        )

        return Response(
            {'message': 'Property saved successfully.'},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)

        saved_property = SavedProperty.objects.filter(
            user=request.user,
            property=property_obj
        ).first()

        if not saved_property:
            return Response(
                {'message': 'Property is not saved.'},
                status=status.HTTP_404_NOT_FOUND
            )

        saved_property.delete()

        return Response(
            {'message': 'Property unsaved successfully.'},
            status=status.HTTP_204_NO_CONTENT
        )
class SavedPropertiesListView(APIView):
    permission_classes = [ArabicIsAuthenticated]

    def initial(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated('الرجاء تسجيل الدخول')

        super().initial(request, *args, **kwargs)

    def get(self, request):
        saved_properties = SavedProperty.objects.filter(
            user=request.user
        ).select_related('property')

        serializer = SavedPropertySerializer(
            saved_properties,
            many=True
        )

        if not saved_properties.exists():
            return Response(
                {
                    'saved_properties': [],
                    'message': 'No saved properties found.'
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'saved_properties': serializer.data
            },
            status=status.HTTP_200_OK
        )

class SharePropertyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)

        if property_obj.status == Property.STATUS_RENTED:
            return Response(
                {'message': 'This property is no longer available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'link': f'https://bayti.ps/property/{property_obj.pk}'
            },
            status=status.HTTP_200_OK
        )

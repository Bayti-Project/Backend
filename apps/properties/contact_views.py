from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.interest_requests.models import InterestRequest
from apps.properties.models import Property


class PropertyContactView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)

        if not property_obj.interest_enabled:
            return Response(
                {
                    'phone_number': property_obj.owner.phone_number,
                    'whatsapp_number': property_obj.owner.whatsapp_number,
                },
                status=status.HTTP_200_OK
            )

        approved_request = InterestRequest.objects.filter(
            tenant=request.user,
            property=property_obj,
            status=InterestRequest.STATUS_APPROVED,
        ).exists()

        if not approved_request:
            return Response(
                {
                    'message': 'Contact information is available only after your interest request is approved.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                'phone_number': property_obj.owner.phone_number,
                'whatsapp_number': property_obj.owner.whatsapp_number,
            },
            status=status.HTTP_200_OK
        )

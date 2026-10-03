from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.interest_requests.models import InterestRequest
from apps.properties.models import Property

from .owner_profile_serializers import (
    OwnerProfileUserSerializer,
    OwnerRecentInterestRequestSerializer,
    OwnerRecentPropertySerializer,
)


class IsOwnerRole(permissions.BasePermission):
    message = 'This endpoint is only available to property owners.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'owner'
        )


class OwnerProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerRole]

    def get(self, request):
        owner = request.user

        properties_qs = Property.objects.filter(owner=owner)
        requests_qs = InterestRequest.objects.filter(owner=owner)

        stats = {
            'total_properties': properties_qs.count(),
            'active_properties': properties_qs.filter(status=Property.STATUS_AVAILABLE).count(),
            'rented_properties': properties_qs.filter(status=Property.STATUS_RENTED).count(),
            'total_interest_requests': requests_qs.count(),
        }

        recent_requests = requests_qs.order_by('-created_at', '-id')[:3]
        recent_properties = properties_qs.order_by('-created_at', '-id')[:3]

        return Response({
            'user': OwnerProfileUserSerializer(owner).data,
            'stats': stats,
            'recent_interest_requests': OwnerRecentInterestRequestSerializer(
                recent_requests, many=True
            ).data,
            'recent_properties': OwnerRecentPropertySerializer(
                recent_properties, many=True
            ).data,
        }, status=status.HTTP_200_OK)
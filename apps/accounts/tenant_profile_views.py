from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.interest_requests.models import InterestRequest
from apps.saved_properties.models import SavedProperty
from apps.saved_properties.serializers import SavedPropertySerializer

from .tenant_profile_serializers import (
    TenantProfileUserSerializer,
    TenantRecentInterestRequestSerializer,
)


class IsTenantRole(permissions.BasePermission):
    message = 'This endpoint is only available to tenants.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == 'tenant'
        )


class TenantProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenantRole]

    def get(self, request):
        tenant = request.user

        requests_qs = InterestRequest.objects.filter(tenant=tenant)
        saved_qs = SavedProperty.objects.filter(user=tenant).select_related('property')

        stats = {
            'total_interest_requests': requests_qs.count(),
            'approved_requests': requests_qs.filter(
                status=InterestRequest.STATUS_APPROVED
            ).count(),
            'rejected_requests': requests_qs.filter(
                status=InterestRequest.STATUS_REJECTED
            ).count(),
            'pending_requests': requests_qs.filter(
                status=InterestRequest.STATUS_PENDING
            ).count(),
            'saved_properties_count': saved_qs.count(),
        }

        recent_requests = requests_qs.order_by('-created_at', '-id')[:3]
        recent_saved = saved_qs.order_by('-created_at', '-id')[:3]

        return Response({
            'user': TenantProfileUserSerializer(tenant).data,
            'stats': stats,
            'recent_interest_requests': TenantRecentInterestRequestSerializer(
                recent_requests, many=True
            ).data,
            'recent_saved_properties': SavedPropertySerializer(
                recent_saved, many=True
            ).data,
        }, status=status.HTTP_200_OK)
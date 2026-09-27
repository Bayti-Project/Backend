from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.interest_requests.models import InterestRequest
from apps.interest_requests.permissions import IsTenant
from apps.interest_requests.serializers import(
    InterestRequestSerializer,
    InterestRequestStatusSerializer,
)
from apps.properties.models import Property
from apps.properties.permissions import IsPropertyOwner

class InterestRequestCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenant]

    def post(self, request, pk):
        property_obj = get_object_or_404(Property, pk=pk)

        if property_obj.owner == request.user:
            raise ValidationError(
                {'detail': 'You cannot send an interest request for your own property.'}
            )

        if property_obj.status == Property.STATUS_RENTED:
            raise ValidationError(
                {'detail': 'This property is rented and cannot receive interest requests.'}
            )

        if InterestRequest.objects.filter(
            tenant=request.user, property=property_obj
        ).exists():
            raise ValidationError(
                {'detail': 'You have already sent an interest request for this property.'}
            )

        try:
            interest_request = InterestRequest.objects.create(
                tenant=request.user,
                property=property_obj,
                owner=property_obj.owner,
            )
        except IntegrityError:
            raise ValidationError(
                {'detail': 'You have already sent an interest request for this property.'}
            )

        serializer = InterestRequestSerializer(interest_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class InterestRequestStatusView(generics.UpdateAPIView):
    queryset = InterestRequest.objects.all()
    serializer_class = InterestRequestStatusSerializer
    permission_classes = [permissions.IsAuthenticated, IsPropertyOwner]
    http_method_names = ['put']

class OwnerInterestRequestListView(generics.ListAPIView):
    serializer_class = InterestRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = InterestRequest.objects.filter(owner=request.user)

        status_param = request.query_params.get('status')
        if status_param:
            valid_statuses = [
                InterestRequest.STATUS_PENDING,
                InterestRequest.STATUS_APPROVED,
                InterestRequest.STATUS_REJECTED,
            ]
            if status_param not in valid_statuses:
                raise ValidationError(
                    {'detail': 'Status must be pending, approved, or rejected.'}
                )
            queryset = queryset.filter(status=status_param)

        queryset = queryset.order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data, 'count': queryset.count()})
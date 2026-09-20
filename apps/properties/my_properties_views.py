from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.properties.models import Property
from apps.properties.serializers.list_serializers import PropertyListSerializer
from apps.properties.search_utils import (
    ELECTRICITY_FIELD_MAP,
    WATER_FIELD_MAP,
    SearchValidationError,
    parse_area_param,
    parse_choice_param,
    parse_decimal_param,
    parse_int_param,
    parse_multi_choice_param,
)


class MyPropertiesView(generics.ListAPIView):
    serializer_class = PropertyListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        params = request.query_params

        try:
            governorate = parse_choice_param(
                params, 'governorate', dict(Property.GOVERNORATE_CHOICES)
            )
            area = parse_area_param(params, governorate)
            property_type = parse_choice_param(
                params, 'property_type', dict(Property.PROPERTY_TYPE_CHOICES)
            )
            bedrooms = parse_int_param(params, 'bedrooms')
            min_price = parse_decimal_param(params, 'min_price')
            max_price = parse_decimal_param(params, 'max_price')
            electricity_fields = parse_multi_choice_param(
                params, 'electricity', ELECTRICITY_FIELD_MAP
            )
            water_fields = parse_multi_choice_param(params, 'water', WATER_FIELD_MAP)
            neighborhood = params.get('neighborhood') or None
            search = params.get('search') or None
        except SearchValidationError as exc:
            raise ValidationError({'detail': exc.message})

        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationError({'detail': "'min_price' cannot be greater than 'max_price'."})

        queryset = Property.objects.filter(owner=request.user)

        if search:
            queryset = queryset.filter(title__icontains=search)
        if governorate:
            queryset = queryset.filter(governorate=governorate)
        if area:
            queryset = queryset.filter(area=area)
        if neighborhood:
            queryset = queryset.filter(neighborhood__icontains=neighborhood)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if bedrooms is not None:
            queryset = queryset.filter(bedrooms=bedrooms)
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        if electricity_fields:
            q = Q()
            for field in electricity_fields:
                q |= Q(**{field: True})
            queryset = queryset.filter(q)
        if water_fields:
            q = Q()
            for field in water_fields:
                q |= Q(**{field: True})
            queryset = queryset.filter(q)

        queryset = queryset.order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data, 'count': queryset.count()})
from rest_framework import serializers

from apps.interest_requests.models import InterestRequest
from .models import User


class TenantProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'whatsapp_number',
            'profile_image',
            'account_type',
            'is_verified',
            'created_at',
        ]
        read_only_fields = fields


class TenantRecentInterestRequestSerializer(serializers.ModelSerializer):
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = InterestRequest
        fields = [
            'id',
            'property_title',
            'property_thumbnail',
            'status',
            'created_at',
        ]
        read_only_fields = fields

    def get_property_thumbnail(self, obj):
        first_image = obj.property.images.first()
        if first_image:
            return first_image.image.url
        return None
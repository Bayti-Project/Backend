from rest_framework import serializers

from apps.interest_requests.models import InterestRequest
from apps.properties.models import Property
from .models import User


class OwnerProfileUserSerializer(serializers.ModelSerializer):
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


class OwnerRecentInterestRequestSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.full_name', read_only=True)
    tenant_image = serializers.ImageField(source='tenant.profile_image', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)

    class Meta:
        model = InterestRequest
        fields = [
            'id',
            'tenant_name',
            'tenant_image',
            'property_title',
            'status',
            'created_at',
        ]
        read_only_fields = fields


class OwnerRecentPropertySerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'address',
            'price',
            'status',
            'thumbnail',
        ]
        read_only_fields = fields

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return first_image.image.url
        return None
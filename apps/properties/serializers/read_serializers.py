from rest_framework import serializers

from apps.properties.models import Property, PropertyImage


class PropertyDetailImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'created_at']


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyDetailImageSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'description',
            'price',
            'address',
            'status',
            'owner',
            'images',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
from rest_framework import serializers

from apps.properties.models import Property


class PropertyListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'price',
            'address',
            'governorate',
            'area',
            'neighborhood',
            'property_type',
            'bedrooms',
            'bathrooms',
            'area_sqm',
            'status',
            'thumbnail',
            'created_at',
        ]
        read_only_fields = fields

    def get_thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return first_image.image.url
        return None
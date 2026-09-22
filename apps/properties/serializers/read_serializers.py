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
            'governorate',
            'area',
            'neighborhood',
            'property_type',
            'bedrooms',
            'bathrooms',
            'area_sqm',
            'has_solar',
            'has_generator_line',
            'has_main_grid',
            'has_water_tank',
            'has_private_well',
            'images',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
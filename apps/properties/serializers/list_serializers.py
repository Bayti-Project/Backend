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
            'has_solar',
            'has_generator_line',
            'has_main_grid',
            'has_water_tank',
            'has_private_well',
            'is_furnished',
            'has_elevator',
            'has_balcony',
            'has_parking',
            'has_central_ac',
            'has_shared_pool',
            'has_gym',
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
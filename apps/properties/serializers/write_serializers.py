from rest_framework import serializers

from apps.properties.models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image']


class PropertyCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )
    uploaded_images = PropertyImageSerializer(source='images', many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'price', 'address',
            'status', 'owner', 'images', 'uploaded_images',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'status', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        property_instance = Property.objects.create(**validated_data)

        for image in images_data:
            PropertyImage.objects.create(property=property_instance, image=image)

        return property_instance

class PropertyEditSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )
    image_ids_to_delete = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )
    uploaded_images = PropertyImageSerializer(source='images', many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'price', 'address',
            'status', 'owner', 'images', 'image_ids_to_delete',
            'uploaded_images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'status', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_image_ids_to_delete(self, value):
        instance = self.instance
        valid_ids = set(instance.images.values_list('id', flat=True))
        invalid_ids = set(value) - valid_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"These image IDs don't belong to this property: {invalid_ids}"
            )
        return value

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', [])
        ids_to_delete = validated_data.pop('image_ids_to_delete', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if ids_to_delete:
            instance.images.filter(id__in=ids_to_delete).delete()

        for image in images_data:
            PropertyImage.objects.create(property=instance, image=image)

        return instance
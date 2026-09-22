from rest_framework import serializers

from apps.properties.models import Property


class PropertyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['status']

    def validate_status(self, value):
        valid_statuses = [
            Property.STATUS_AVAILABLE,
            Property.STATUS_RESERVED,
            Property.STATUS_RENTED,
        ]

        if value not in valid_statuses:
            raise serializers.ValidationError(
                "Status must be available, reserved, or rented."
            )

        return value
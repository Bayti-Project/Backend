from rest_framework import serializers

from apps.properties.serializers.list_serializers import PropertyListSerializer
from apps.saved_properties.models import SavedProperty


class SavedPropertySerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)

    class Meta:
        model = SavedProperty
        fields = [
            'property',
            'created_at',
        ]
        read_only_fields = fields
        
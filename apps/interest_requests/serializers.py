from rest_framework import serializers

from apps.interest_requests.models import InterestRequest


class InterestRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestRequest
        fields = [
            'id',
            'tenant',
            'property',
            'owner',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

class InterestRequestStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True)
    class Meta:
        model = InterestRequest
        fields = ['status']

    def validate_status(self, value):
        allowed = (InterestRequest.STATUS_APPROVED, InterestRequest.STATUS_REJECTED)
        if value not in allowed:
            raise serializers.ValidationError("Status must be approved or rejected.")
        return value

    def to_representation(self, instance):
        return InterestRequestSerializer(instance).data
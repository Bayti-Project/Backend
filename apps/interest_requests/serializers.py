from rest_framework import serializers

from apps.interest_requests.models import InterestRequest


class InterestRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestRequest
        fields = [
            'id',
            'request_code',
            'tenant',
            'property',
            'owner',
            'status',
            'rejection_reason',
            'rejection_note',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

class InterestRequestStatusSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=True)
    class Meta:
        model = InterestRequest
        fields = ['status', 'rejection_reason', 'rejection_note']

    def validate_status(self, value):
        allowed = (InterestRequest.STATUS_APPROVED, InterestRequest.STATUS_REJECTED)
        if value not in allowed:
            raise serializers.ValidationError("Status must be approved or rejected.")
        return value

    def validate(self, attrs):
        if attrs.get('status') == InterestRequest.STATUS_REJECTED:
            if not attrs.get('rejection_reason'):
                raise serializers.ValidationError(
                    {'rejection_reason': 'This field is required when rejecting a request.'}
                )
        else:
            attrs.pop('rejection_reason', None)
            attrs.pop('rejection_note', None)
        return attrs
    
    def to_representation(self, instance):
        return InterestRequestSerializer(instance).data
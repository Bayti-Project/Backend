from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=[('owner', 'مالك عقار'), ('tenant', 'مستأجر')]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'phone_number',
            'password',
            'confirm_password',
            'role',
            'account_type',
            'profile_image',
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': True,
            },
            'full_name': {
                'required': True,
            },
            'email': {
                'required': True,
            },
            'phone_number': {
                'required': True,
            },
            'account_type': {
                'required': True,
            },
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "This phone number is already registered."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')

        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        attrs['user'] = user
        return attrs    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email',
            'phone_number',
            'whatsapp_number',
            'profile_image',
            'role',
            'account_type',
        ]
        read_only_fields = ['id', 'email', 'role', 'account_type']

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })
        return attrs
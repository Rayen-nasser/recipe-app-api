"""
Serializers for the user API View
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _  # For handling translations.

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'name', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        """Create and return a new user with encrypted password."""
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """Update and return the user with encrypted password, if provided."""
        password = validated_data.pop('password', None)

        # Update the instance using the validated data (excluding password).
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for user authentication."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate user."""
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )
        if email and password and not user:
            msg = _('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

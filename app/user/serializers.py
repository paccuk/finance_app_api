"""
Serializers for the user API.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

from rest_framework_simplejwt.serializers import TokenObtainSerializer, PasswordField


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', ]
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create and return a user with encrypted data."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class TokenObtainPairSerializer(TokenObtainSerializer):
    """Serializer for the user auth token."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.EmailField()
        self.fields["password"] = PasswordField()

""" Serializers for the user API view"""

from django.contrib.auth import (
    get_user_model,
    authenticate)
from django.utils.translation import gettext as _
from rest_framework import serializers
from core import models
from django.utils import timezone


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'first_name', 'last_name',
                  'phone_number', 'city', 'bio', 'studio',
                  'password', 'last_login', 'created_at']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}
        read_only_fields = ['id', 'last_login', 'created_at']

    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return a user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        user.updated_at = timezone.now()
        user.save(update_fields=['updated_at'])
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate user with provided credentials')
            raise serializers.ValidationError(msg, code='authorization')
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        attrs['user'] = user
        return attrs


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserImage
        fields = ['id', 'user_id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {
            'image': {'required': True},
            'user_id': {'required': True}
            }

"""Views for the user API"""

from rest_framework import generics, authentication, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.settings import api_settings
from user.serializers import (UserSerializer, AuthTokenSerializer, UserImageSerializer)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from core.models import UserImage
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer



class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the updated user"""
        return self.request.user

class UserImageUploadViewSet(viewsets.ModelViewSet):
    """Upload an image for the user"""
    serializer_class = UserImageSerializer
    queryset = UserImage.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user)

    def create(self, request, *args, **kwargs):
        # Check if a profile image already exists for the user
        existing_image, created = UserImage.objects.get_or_create(user_id=request.user)
        # If an image already exists, update it; otherwise, create a new one
        serializer = self.get_serializer(existing_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

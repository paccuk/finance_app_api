"""
Views for the user API.
"""
from rest_framework_simplejwt import authentication

from rest_framework import generics, permissions

from .serializers import (
    UserSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = [permissions.BasePermission]


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the user."""
        return self.request.user

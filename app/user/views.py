# Import necessary modules and classes from the rest_framework library
from rest_framework import generics, authentication, permissions
# Import the base class for creating views that handle HTTP POST requests
from rest_framework.authtoken.views import ObtainAuthToken
# Import the API settings from Django REST framework for global settings
from rest_framework.settings import api_settings

# Import the serializers we defined for user and token creation
from user.serializers import (
    UserSerializer,  # Serializer to handle user data
    AuthTokenSerializer  # Serializer to handle authentication token data
)


class CreateUserView(generics.CreateAPIView):
    """
    View for creating a new user in the system.
    It uses the UserSerializer to validate and save user data.
    """
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """
    View for creating an auth token for the user.
    The user provides credentials (email, password) to obtain a token.
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageTokenView(generics.RetrieveUpdateAPIView):
    """
    View for managing the user's auth token.
    """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Return the authenticated user.
        """
        return self.request.user

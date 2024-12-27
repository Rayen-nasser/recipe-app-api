from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe.serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting recipes.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = [TokenAuthentication]

    # Custom permission logic
    def get_permissions(self):
        if self.action == 'list':  # Allow unauthenticated users to access the list
            return []  # No permissions required for 'GET' request (list)

        # Enforce authentication for other actions (POST, PUT, DELETE)
        return [
            IsAuthenticated(),
        ]

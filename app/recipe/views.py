"""
View for the recipe APIs
"""
from rest_framework import (viewsets, mixins)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagsSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting recipes.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer  # Using the imported serializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer for the authenticated user."""
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

class TagViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin ,mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Serializer for Tag objects."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
   # Current logic
    def get_queryset(self):
        """Retrieve tags for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


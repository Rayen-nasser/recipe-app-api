from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)

from rest_framework import (viewsets, mixins, status)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import (
    Recipe,
    Tag,
    Ingredient
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagsSerializer,
    IngredientsSerializer,
    RecipeImageSerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="Retrieve a list of recipes",
        description=(
            "Fetch a list of recipes from the"
            "database. You can filter the results "
            "by specifying tags and ingredients as query parameters."
            "The parameters should be comma-separated"
            "integers representing the IDs of tags or ingredients."
        ),
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, creating, retrieving, updating, and deleting recipes.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer  # Using the imported serializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """ convert a list of strings to integer """
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Return recipes for authenticated user"""
        # First filter by user
        queryset = self.queryset.filter(user=self.request.user)

        # Get query parameters
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')

        if tags:
            tag_ids = self._params_to_ints(tags)
            # Use OR condition for tags
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            # Use OR condition for ingredients
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.distinct().order_by('-id')

    def get_serializer_class(self):
        """Return the serializer for the authenticated user."""
        if self.action == 'list':
            return RecipeSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload_image')
    def upload_image(self, request, pk=None):
        """Upload an image to the recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(instance=recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description=(
                    "Filter by assigned recipes."
                    "Provide `1` to only include tags "
                    "or ingredients that are assigned to recipes."
                ),
            ),
        ]
       ),
)
class BaseRecipeAttrViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Base class for recipe attributes (tags, ingredients).
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve tags for the authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipes__isnull=False)
        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Serializer for Tag objects."""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Serializer for Ingredient objects."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer

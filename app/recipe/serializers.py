from rest_framework import serializers
from core.models import Recipe, Tag, Ingredient


class TagsSerializer(serializers.ModelSerializer):
    """Serializer for Tag objects."""
    class Meta:
        model = Tag
        fields = ['id', 'name']

    def create(self, validated_data):
        """Create a Tag with the user context."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class IngredientsSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient objects."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'measurement']

    def create(self, validated_data):
        """Create an Ingredient with the user context."""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe objects."""
    tags = TagsSerializer(many=True, required=False)
    ingredients = IngredientsSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes',
            'price', 'link', 'tags', 'ingredients',
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags_data, recipe):
        """Helper method to get or create tags."""
        if tags_data:
            for tag_data in tags_data:
                tag_obj, created = Tag.objects.get_or_create(
                    user=recipe.user,
                    **tag_data
                )
                recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients_data, recipe):
        """Helper method to get or create tags."""
        if ingredients_data:
            for ingredient_data in ingredients_data:
                ingredient_obj, created = Ingredient.objects.get_or_create(
                    user=recipe.user,
                    **ingredient_data
                )
                recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a new Recipe."""
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags_data, recipe)
        self._get_or_create_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update an existing Recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe objects with extra details."""
    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields + ['description', 'image']


class RecipeImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    """Serializer for Recipe Image objects."""
    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
# Add a blank line at the end of the file

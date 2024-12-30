from rest_framework import serializers
from core.models import Recipe, Tag


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']  # Include the user field

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe objects."""
    tags = TagsSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'time_minutes', 'price', 'link', 'tags'
        ]
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags_data, recipe):
        """Helper to get or create existing tags."""
        for tag_data in tags_data:
            tag_obj, created = Tag.objects.get_or_create(
                user=recipe.user,
                **tag_data
            )
            recipe.tags.add(tag_obj)

    def create(self, validated_data):
        """Create a new recipe."""
        tags_data = validated_data.pop('tags', [])
        # validated_data['user'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags_data, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update an existing recipe."""
        tags = validated_data.pop('tags', [])
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, key in validated_data.items():
            setattr(instance, attr, key)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe objects with extra details."""
    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields
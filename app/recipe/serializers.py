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

    def create(self, validated_data):
        """Create a new recipe."""
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user

        # Handle tags
        for tag_data in tags_data:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag_data
            )

            recipe.tags.add(tag_obj) # are if tag exit will not add to database ?

        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe objects with extra details."""
    class Meta(RecipeSerializer.Meta):
        model = Recipe
        fields = RecipeSerializer.Meta.fields
"""
Test for recipe API.
"""
from decimal import Decimal
import tempfile
import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


from PIL import Image
from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Return the URL for uploading an image."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a new recipe."""
    defaults = {
        'title': 'sample recipe title',
        'time_minutes': 10,
        'price': Decimal('5.50'),
        'description': 'sample recipe description',
        'link': 'http://example.com/recipe'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(
        user=user,
        **defaults
    )  # Create method from serializer recipe
    return recipe


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipe(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.post(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='password123',
            name='Test User'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(self.user)
        create_recipe(self.user, title='Sample Recipe 2')

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test retrieving recipes for user."""
        user2 = create_user(
            email='test2@example.com',
            password='password456',
            name='Test User 2'
        )
        create_recipe(user2)
        create_recipe(self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test retrieving a single recipe detail."""
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe."""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 60,
            'price': Decimal('15.99'),
            'description': 'This is a test recipe.',
            'link': 'http://example.com/test-recipe'
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test updating a recipe with a patch request."""
        recipe = create_recipe(self.user)
        payload = {'title': 'Updated Recipe'}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_update_user_returns_error(self):
        """Test updating a recipe with a new user returns an error."""
        new_user = create_user(email='user99@gmail.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)  # Ensure user didn't change

    def test_recipe_other_users_error(self):
        """Test retrieving a recipe from a different user returns an error."""
        new_user = create_user(email='user99@gmail.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 60,
            'price': Decimal('15.99'),
            'description': 'This is a test recipe.',
            'link': 'http://example.com/test-recipe',
            'tags': [{'name': 'foo'}, {'name': 'fruit'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        for tag_data in payload['tags']:
            tag = Tag.objects.get(name=tag_data['name'], user=self.user)
            self.assertIn(tag, recipe.tags.all())

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tags."""
        tag_fruit = Tag.objects.create(name="fruit", user=self.user)
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 60,
            'price': Decimal('15.99'),
            'description': 'This is a test recipe.',
            'link': 'http://example.com/test-recipe',
            'tags': [
                {'name': 'foo'},
                {'name': 'fruit'}
            ]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_fruit, recipe.tags.all())
        tag_foo = Tag.objects.get(name='foo', user=self.user)
        self.assertIn(tag_foo, recipe.tags.all())

    def test_create_tag_on_update(self):
        """Test creating a tag when updating a recipe."""
        recipe = Recipe.objects.create(
            user=self.user,
            title='Test Recipe',
            time_minutes=60,
            price=Decimal('15.99'),
            description='This is a test recipe.',
            link='http://example.com/test-recipe'
        )
        payload = {
            'tags': [{'name': 'foo'}, {'name': 'fruit'}]
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.tags.count(), 2)

    def test_clear_recipe_tags(self):
        """Test clearing a recipe tags"""
        tag = Tag.objects.create(name='foo', user=self.user)
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a new recipe with new ingredients"""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 60,
            'price': Decimal('15.99'),
            'description': 'This is a test recipe.',
            'link': 'http://example.com/test-recipe',
            'ingredients': [
                {'name': 'apple', 'quantity': 2},
                {'name': 'banana', 'quantity': 2}
            ],
            'tags': [{'name': 'fruit'}]
        }
        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data['ingredients'][0]['name'], 'apple')
        self.assertEqual(res.data['ingredients'][1]['name'], 'banana')

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a new recipe with existing ingredients"""
        Ingredient.objects.create(name='apple', user=self.user)
        Ingredient.objects.create(name='banana', user=self.user)

        payload = {
            'title': 'Test Recipe',
            'time_minutes': 60,
            'price': Decimal('15.99'),
            'description': 'This is a test recipe.',
            'link': 'http://example.com/test-recipe',
            'ingredients': [
                {'name': 'apple', 'quantity': 2},
                {'name': 'banana', 'quantity': 2},
            ],
            'tags': [{'name': 'fruit'}],
        }

        res = self.client.post(RECIPE_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe_id = res.data.get('id')
        recipe = Recipe.objects.get(id=recipe_id)

        ingredient_names = [
            ingredient.name for ingredient in recipe.ingredients.all()
            ]
        self.assertIn('apple', ingredient_names)
        self.assertIn('banana', ingredient_names)

    def test_create_ingredient_on_update(self):
        """Test updating a recipe with new ingredients"""
        recipe = create_recipe(user=self.user)
        payload = {
            'ingredients': [
                {'name': 'apple', 'quantity': 3},
                {'name': 'banana', 'quantity': 3}
            ]
        }
        url = detail_url(
            recipe_id=recipe.id
        )
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertEqual(recipe.ingredients.get(name='apple').quantity, 3)
        self.assertEqual(recipe.ingredients.get(name='banana').quantity, 3)

    def test_clear_recipe_ingredients(self):
        """Test clearing the ingredients of a recipe"""
        recipe = create_recipe(user=self.user)
        ingredient1 = Ingredient.objects.create(name='apple', user=self.user)
        ingredient2 = Ingredient.objects.create(name='banana', user=self.user)
        recipe.ingredients.add(ingredient1, ingredient2)

        payload = {'ingredients': []}
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

class ImageUpdateTestCase(TestCase):
    """Test for upload images API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'testuser',
            'testpass'
            )
        self.recipe = create_recipe(user=self.user)
        self.client.force_authenticate(self.user)

    def  tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_invalid_image(self):
        """Test uploading an invalid image file"""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'invalid_image_file.txt'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
# Add a blank line at the end of the file

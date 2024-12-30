"""
Tests for Ingredient API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientsSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

def create_user(email="user@example.com", password="password123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)

def detail_url(ingredient_id=None):
    """Return the URL for the ingredient model."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientApiTests(TestCase):
    """Test unauthenticated tag API access."""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """Test that authentication is required."""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test authenticated ingredient API access."""
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Apple', quantity=2, measurement=None)
        Ingredient.objects.create(user=self.user, name='Banana', quantity=2, measurement=None)

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.filter(user=self.user).order_by('-name')  # Fixed QuerySet
        serializer = IngredientsSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of Ingredient is limited to authenticated user."""
        user2 = create_user(email="user2@example.com", password="password123")
        Ingredient.objects.create(user=user2, name='Orange', quantity=1, measurement=None)
        ingredient = Ingredient.objects.create(user=self.user, name='Apple', quantity=2, measurement=None)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Apple', quantity=2, measurement=None)
        payload = {'name': 'Updated Apple', 'quantity': 3, 'measurement': 'kg'}
        url = detail_url(ingredient.id)
        res = self.client.put(url, payload)

        ingredient.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])
        self.assertEqual(ingredient.quantity, payload['quantity'])
        self.assertEqual(ingredient.measurement, payload['measurement'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Apple', quantity=2, measurement=None)
        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())
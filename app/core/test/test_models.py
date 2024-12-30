"""
Tests for models
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email="user@gmail.com", password="password"):
    """Helper function to create a user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email is successful"""
        email = "test@gmail.com"
        password = "password1234567890"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_with_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(email, "password123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_without_email_raises_error(self):
        """Test creating a new user without an email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        email = "admin@example.com"
        password = "password1234567890"
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe"""
        user = create_user(
            email='test@example.com',
            password='password123',
        )
        recipe = models.Recipe.objects.create(
            title='Test Recipe',
            user=user,
            time_minutes=10,
            price=Decimal('9.99'),
            description='Test Recipe'
        )
        self.assertEqual(recipe.title, recipe.title)

    def test_create_tag(self):
        """Test creating a recipe"""
        user = create_user()
        tag = models.Tag.objects.create(
            name='Vegan',
            user=user,
        )
        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            name='Flour',
            user=user,
            quantity=2,
            measurement='cups'
        )
        self.assertEqual(str(ingredient), ingredient.name)

# Ensure the file ends with a newline

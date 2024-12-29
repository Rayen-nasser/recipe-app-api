"""
Tests for Tag API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
from recipe.serializers import TagSerializer

TAG_URL = reverse('tag:tag-list')


def create_user(email="user@example.com", password="password123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagApiTests(TestCase):
    """Test unauthenticated tag API access."""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        """Test that authentication is required."""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTests(TestCase):
    """Test authenticated tag API access."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        # Create tags in the database
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # Perform GET request to retrieve tags
        res = self.client.get(TAG_URL)

        # Fetch tags from the database
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        # Verify the response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_tags(self):
        """Test that tags are limited to the authenticated user."""
        user2 = create_user(email='test2@example.com', password='password456')
        Tag.objects.create(user=user2, name='Gluten-free')
        tag = Tag.objects.create(user=self.user, name='Gluten-free')

        # Authenticate as user1 and retrieve tags
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

        # Authenticate as user2 and retrieve tags
        user2_client = APIClient()
        user2_client.force_authenticate(user2)
        res = user2_client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)
        
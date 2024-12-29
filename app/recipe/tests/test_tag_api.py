"""
Tests for Tag API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
from recipe.serializers import TagsSerializer

TAG_URL = reverse('recipe:tag-list')


def create_user(email="user@example.com", password="password123"):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)

def detail_url(tag_id=None):
    """Return the URL for the tag model."""
    return reverse('recipe:tag-detail', args=[tag_id])

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
        serializer = TagsSerializer(tags, many=True)

        # Verify the response
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_tags(self):
        """Test that tags are limited to the authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'password123'
        )
        Tag.objects.create(user=other_user, name='OtherTag')
        Tag.objects.create(user=self.user, name='MyTag')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.filter(user=self.user)
        serializer = TagsSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_update_tags(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        payload = {'name': 'Brunch'}

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        tag.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])


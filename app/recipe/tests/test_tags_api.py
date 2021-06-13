from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagApiTests(TestCase):
    """Test the authorised user tag api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'whafeez21@gmail.com',
            'Password1'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def tes_tags_limited_to_user(self):
        """Test that tags returned are limited to authenticated user"""
        user2 = get_user_model().objects.create_user(
            'test@whbx.io',
            'password'
        )
        Tag.objects.create(user=user2, name='Olive')
        tag = Tag.objects.create(user=self.user, name='Chicko')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test Creating a new tag"""
        payload = {'name': 'Vegitable'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        "Test if tag is inavlid at creation"
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='whafeez21@gmail.com', password='Password1'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Testing databse entries."""

    def test_create_user_with_email_successful(self):
        """Test user creation with email address and password"""
        email = "whafeez21@gmail.com"
        password = "Password1"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalise(self):
        """Testing if the email address of the user is normalised or not"""
        email = "whafeez21@GMAIL.COM"
        user = get_user_model().objects.create_user(email, '12345')
        self.assertEqual(user.email, email.lower())

    def test_new_user_valid_email_address(self):
        """Testing if user have entered email address or not"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', '12345')

    def test_create_news_super_user(self):
        """Testing creation of new super user"""
        user = get_user_model().objects.create_superuser(
            'whafeez22@gmail.com',
            '12345'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Olive'
        )

        self.assertEqual(str(ingredient), ingredient.name)

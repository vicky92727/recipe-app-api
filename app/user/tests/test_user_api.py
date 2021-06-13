from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """Help function to create new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the user api public."""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating a valid user with payload successfully"""
        payload = {
            'email': 'whafeez21@gmail.com',
            'password': 'Password1',
            'name': 'Waqas',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exist(self):
        "Testing if user already exist"
        payload = {
                    'email': 'whafeez21@gmail.com',
                    'password': 'Password1',
                    'name': 'Waqas',
                }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Testing user entered password is too short"""
        payload = {
            'email': 'whafeez21@gmail.com',
            'password': 'pw',
            'name': 'Waqas',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for a user"""
        payload = {"email": 'vicky@gmail.com', 'password': 'Password1'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """test that token is not created if credentials are invalid"""
        create_user(email="whafeez21@gmail.com", password="Password1")
        payload = {"email": "whafeez21@gmail.com", "password": "password1"}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_not_user(self):
        """test that token is not generated if user doesn't exist"""
        payload = {"email": "whafeez21@gmail.com", "password": "Password1"}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test that email and password are required fields"""
        payload = {'email': 'one', 'password': ''}
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authenticationn."""

    def setUp(self):
        self.user = create_user(
            email='whafeez21@gmail.com',
            password='Password1',
            name='Waqas Hafeez'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for loged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test that POST is not allowed on me URL"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {'name': 'Waqas', 'password': 'password123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

"""Tests for the user api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

import tempfile
import os
from PIL import Image
from core.models import UserImage

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
IMAGE_URL = reverse('user:upload-list')
def image_upload_url(user_id):
    """Create and return the user image upload url"""
    return reverse('user:upload-detail', args=[user_id])

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests for the public features of the user api"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        payload = {
            'email': 'test@example.com',
            'first_name': 'test',
            'last_name': 'name',
            'phone_number': '2404100394',
            'password': 'testpass123',
            'city': 'Los Angeles',
            'bio': 'Hi! I am testing',
            'studio': 'Good music studio'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'test ',
            'last_name': 'name',
            'phone_number': '8052345678'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'first_name': 'test ',
            'last_name': 'name',
            'phone_number': '8052345678'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
            ).exists()
        self.assertFalse(user_exists)

    user_details = {
            'first_name': 'test ',
            'last_name': 'name',
            'phone_number': '8052345678',
            'email': 'test@example.com',
            'password': 'test-user-password123'
        }

    def test_create_token_for_user(self):
        """ Test generates token for valid credentials """

        create_user(**self.user_details)

        payload = {
            'email': self.user_details['email'],
            'password': self.user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        create_user(**self.user_details)
        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)

    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error"""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""
    def setUp(self):
        self.user = create_user(email='test@example.com',
                                password='testpass123',
                                first_name='test ',
                                last_name='name',
                                phone_number='8052345678')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
                        'email': 'test@example.com',
                        'first_name': 'test ',
                        'last_name': 'name',
                        'phone_number': '+18052345678',
                        'city': None,
                        'bio': None,
                        'studio': None})

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for the authenticated user"""
        payload = {'first_name': 'updated name', 'password': 'newpassword'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)



class ImageUploadTests(TestCase):
    """Tests for the image upload API"""

    def setUp(self):
        self.client=APIClient()
        self.user = create_user(email='test@example.com',
                                first_name='Joe',
                                last_name='Smith',
                                phone_number='8054394923',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def tearDown(self):
        UserImage.objects.filter(user_id=self.user.id).delete()

    def test_upload_image(self):
        """Test uploading an image to user"""
        # url = image_upload_url(self.user.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10,10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'user_id':self.user.id, 'image': image_file}
            res = self.client.post(IMAGE_URL, payload, format='multipart')

        # self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', res.data)
        # self.assertTrue(os.path.exists(res.data['image'].path))

    def test_upload_image_bad_request(self):
        """Test uploading invalid image to user"""
        # url = image_upload_url(self.user.id)
        payload = {'user_id':self.user.id, 'image': 'notanimage'}
        res = self.client.post(IMAGE_URL, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reupload_image(self):
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file1:
            img = Image.new('RGB', (10,10))
            img.save(image_file1, format='JPEG')
            image_file1.seek(0)
            payload = {'user_id':self.user.id, 'image': image_file1}
            res1 = self.client.post(IMAGE_URL, payload, format='multipart')
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file2:
            img = Image.new('RGB', (10,10))
            img.save(image_file2, format='JPEG')
            image_file2.seek(0)
            payload = {'user_id':self.user.id, 'image': image_file2}
            res2 = self.client.post(IMAGE_URL, payload, format='multipart')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', res2.data)
        self.assertNotEqual(res1.data, res2.data)
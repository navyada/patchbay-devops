"""Tests for listing api"""

from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Listing,
    Category
    )
from listing.serializers import (
    ListingSerializer,
    ListingDetailSerializer
    )

LISTINGS_URL = reverse('listing:listing-list')
READ_LISTINGS_URL = reverse('listing:listingreadonly-list')
CATEGORY_URL = reverse('listing:category-list')
READ_CATEGORY_URL = reverse('listing:categoryreadonly-list')

def detail_url(id):
    """Create and return URL for detailed listing"""
    return reverse('listing:listing-detail', args=[id])

def create_listing(user, **params):
    """Create and return a sample listing"""
    default = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description'
    }
    default.update(params)
    listing = Listing.objects.create(user=user, **default)
    return listing

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicCategoryAPITests(TestCase):
    """Test unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_not_required(self):
        res = self.client.get(READ_CATEGORY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
class PrivateListingAPITests(TestCase):
    """Test authenticated API Requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
                                email='test@example.com',
                                first_name='Joe',
                                last_name='Smith',
                                phone_number='8054394923',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def test_create_category_error(self):
            """Test creating a category"""
            payload = {'name': 'Parent' }
            res = self.client.post(CATEGORY_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPrivateCategoryAPITests(TestCase):
    """Test admin authenticated API Requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
                                email='test@example.com',
                                first_name='Joe',
                                last_name='Smith',
                                phone_number='8054394923',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def test_create_category_successful(self):
            """Test creating a category"""
            payload = {'name': 'Parent' }
            res = self.client.post(CATEGORY_URL, payload)
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            payload = {'name': 'Child', 'parent_category': res.data['id']}
            child = self.client.post(CATEGORY_URL, payload)
            self.assertEqual(child.status_code, status.HTTP_201_CREATED)
            self.assertEqual(len(Category.objects.all()), 2)

    def test_read_category_successful(self):
        payload = {'name': 'Parent' }
        res = self.client.post(CATEGORY_URL, payload)
        res = self.client.get(CATEGORY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_category(self):
        """Test updating a category"""
        category = Category.objects.create(name='Name')
        payload = {'name':'New Name'}
        url = reverse('listing:category-detail', args=[category.id])
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, payload['name'])

    def test_delete_category(self):
        """Test deleting a category"""
        category = Category.objects.create(name='Category')
        url = reverse('listing:category-detail', args=[category.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        categories = Category.objects.filter(name='Category')
        self.assertFalse(categories.exists())

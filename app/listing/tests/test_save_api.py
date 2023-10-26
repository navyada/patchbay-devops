"""
Test that users can save listings
"""
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
    Category,
    Address,
    Saved
    )
from listing.serializers import (
    ListingSerializer,
    ListingDetailSerializer,
    SavedSerializer
    )

SAVED_URL = reverse('listing:saved-list')
def detail_url(id):
    """Create and return URL for detailed listing"""
    return reverse('listing:listing-detail', args=[id])

def create_listing(user, **params):
    """Create and return a sample listing"""
    default = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description',
        'address': {'address_1':'1197 W 37th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
    }
    default.update(params)
    address = default.pop('address', None)
    address, created = Address.objects.get_or_create(**address)
    listing = Listing.objects.create(user=user, address=address, **default)
    return listing

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

class PublicSavedApiTests(TestCase):
    """Test unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving saved listings"""
        res = self.client.get(SAVED_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateSavedAPITests(TestCase):
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

    def test_save_listing(self):
        user = create_user(email='test1@example.com', first_name='Mary', last_name='Jane', phone_number='8054394922', password='Test12356')
        listing = create_listing(user=user)
        payload = {'user': self.user.id, 'listing': listing.id}
        res = self.client.post(SAVED_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Saved.objects.count(), 1)

    def test_delete_saved_listing(self):
        """Test unsaving a listing"""
        user = create_user(email='test1@example.com', first_name='Mary', last_name='Jane', phone_number='8054394922', password='Test12356')
        listing = create_listing(user=user)
        saved = Saved.objects.create(user=self.user, listing=listing)
        url = reverse('listing:saved-detail', args=[saved.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_only_users_saved_listing(self):
        """Test list is limited to authenticated user"""
        user = create_user(email='test1@example.com', first_name='Mary', last_name='Jane', phone_number='8054394922', password='Test12356')
        listing = create_listing(user=user)
        Saved.objects.create(user=user, listing=listing)
        Saved.objects.create(user=self.user, listing=listing)
        self.assertEqual(Saved.objects.count(), 2)
        res = self.client.get(SAVED_URL)
        self.assertEqual(len(res.data), 1)
        self.assertTrue(res.data[0]['user'], self.user)
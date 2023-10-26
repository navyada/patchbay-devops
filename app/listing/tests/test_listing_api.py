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
    Category,
    Address
    )
from listing.serializers import (
    ListingSerializer,
    ListingDetailSerializer,
    AddressSerializer
    )

LISTINGS_URL = reverse('listing:listing-list')
READ_LISTINGS_URL = reverse('listing:listingreadonly-list')

def detail_url(id):
    """Create and return URL for detailed listing"""
    return reverse('listing:listing-detail', args=[id])

def create_listing(user, **params):
    """Create and return a sample listing"""
    default = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description',
        'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
    }
    default.update(params)
    address = default.pop('address', None)
    address, created = Address.objects.get_or_create(**address)
    listing = Listing.objects.create(user=user, address=address, **default)
    return listing

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicListingAPITests(TestCase):
    """Test unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(LISTINGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_view_only(self):
        """Test if view is allowed with no user authentication"""
        user = create_user(email='test1@example.com',
                                first_name='Joey',
                                last_name='Smith',
                                phone_number='8053394923',
                                password='testpass123')
        create_listing(user=user)
        res = self.client.get(READ_LISTINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_update_delete_in_view_only_error(self):
        """Test that you cannot post/patch/delete anything from read only view"""
        payload = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description',
        'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
    }
        res = self.client.post(READ_LISTINGS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        user = create_user(email='test1@example.com',
                                first_name='Joey',
                                last_name='Smith',
                                phone_number='8053394923',
                                password='testpass123')
        listing = create_listing(user=user)
        payload = {'title':'new title'}
        url = reverse('listing:listing-detail', args=[listing.id])
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateListingAPITests(TestCase):
    """Test authenticated API Requests"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='test@example.com',
                                first_name='Joe',
                                last_name='Smith',
                                phone_number='8054394923',
                                password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_listings(self):
        """Test retriving a list of listings"""
        create_listing(user=self.user)
        create_listing(user=self.user)
        res = self.client.get(LISTINGS_URL)

        listings = Listing.objects.all().order_by('-id')
        serializer = ListingSerializer(listings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_listing_list_limited_to_user(self):
        """Test list of listings is limited to authenticated users"""
        other_user =  create_user(email='test1@example.com',
                                first_name='Joey',
                                last_name='Smith',
                                phone_number='8053394923',
                                password='testpass123')
        create_listing(user=other_user)
        create_listing(user=self.user)

        res = self.client.get(LISTINGS_URL)
        listings = Listing.objects.filter(user=self.user)
        serializer = ListingSerializer(listings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_listing_details(self):
        """Test retriving a list of listings"""
        listing = create_listing(user=self.user,
                       replacement_value=Decimal('100.00'),
                       make='Fender',
                       year=2021
                       )
        url = detail_url(listing.id)
        res = self.client.get(url)
        serializer = ListingDetailSerializer(listing)
        self.assertEqual(res.data, serializer.data)

    def test_create_listing(self):
        """Test creating a listing"""
        payload = {
            'title': 'sample listing',
            'price_cents': 10000,
            'description':'sample description',
            'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
        }
        res = self.client.post(LISTINGS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        listing = Listing.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'address':
                self.assertTrue(Address.objects.filter(address_1=v['address_1']).exists())
            else:
                self.assertEqual(getattr(listing, k), v)
        self.assertEqual(listing.user, self.user)

    def test_create_listing_with_address(self):
        """Test creating a listing"""
        payload = {
            'title': 'sample listing',
            'price_cents': 10000,
            'description':'sample description',
            'address': {'address_1': '1129 W 3th St',
                         'city': 'Los Angeles',
                         'state': 'CA',
                         'zip_code': '90007'}
        }
        res = self.client.post(LISTINGS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        listing = Listing.objects.get(id=res.data['id'])
        self.assertEqual(listing.user, self.user)


    def test_partial_update(self):
        """Test partial update of a listing"""
        original_price = 500
        listing = create_listing(user=self.user, price_cents=original_price)
        payload = {'title': 'New listing title'}
        url = detail_url(listing.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        listing.refresh_from_db()
        self.assertEqual(listing.title, payload['title'])
        self.assertEqual(listing.price_cents, original_price)
        self.assertEqual(listing.user, self.user)

    def test_full_update(self):
        """Test full update of listing"""
        original_price = 500
        listing = create_listing(
            user=self.user,
            title='Sample title',
            price_cents=original_price
        )

        payload = {
            'title': 'new title',
            'price_cents':600,
            'address': {'address_1':'1197 W 37th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
        }
        url = detail_url(listing.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        listing.refresh_from_db()
        for k,v in payload.items():
            if k =='address':
                self.assertTrue(Address.objects.filter(address_1 = payload['address']['address_1']).exists())
            else:
                self.assertEqual(getattr(listing, k), v)
        self.assertEqual(listing.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the listing user results in error"""
        new_user = create_user(email='new@example.com',
                               password='123455',
                               first_name='John',
                               last_name='Smith',
                               phone_number='2402345642')
        listing = create_listing(user=self.user)

        payload = {'user':new_user.id}
        url = detail_url(listing.id)
        self.client.patch(url, payload)
        listing.refresh_from_db()

        self.assertEqual(listing.user, self.user)

    def test_update_other_user_listing_returns_error(self):
        """Test changing the listing user results in error"""
        new_user = create_user(email='new@example.com',
                               password='123455',
                               first_name='John',
                               last_name='Smith',
                               phone_number='2402345642')
        listing = create_listing(user=new_user)

        payload = {'title':'New title'}
        url = detail_url(listing.id)
        self.client.patch(url, payload)
        listing.refresh_from_db()
        self.assertNotIn(payload['title'], listing.title)

    def test_delete_listing(self):
        """Test deleting a listing successful"""
        listing = create_listing(user=self.user)
        url = detail_url(listing.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(id=listing.id).exists())

    def test_delete_other_user_listing_error(self):
        """Test trying to delete another user's listing gives error"""
        new_user = create_user(email='new@example.com',
                               password='123455',
                               first_name='John',
                               last_name='Smith',
                               phone_number='2402345642')
        listing = create_listing(user=new_user)

        url = detail_url(listing.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Listing.objects.filter(id=listing.id).exists())

    def test_creating_listing_with_category(self):
        """Test creating a listing with a category"""
        category = Category.objects.create(name='Drums')
        payload = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description',
        'category': [category.id],
        'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
        }
        res = self.client.post(LISTINGS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_filtering_listing_with_category(self):
        """Test filtering a listing with a category"""
        category = Category.objects.create(name='Drums')
        c1 = create_listing(user=self.user)
        c2 = create_listing(user=self.user, title='Sample2')
        c2.category.add(category)
        s1 = ListingSerializer(c1)
        s2 = ListingSerializer(c2)
        params = {'category': f'{category.id}'}
        res = self.client.get(LISTINGS_URL, params)
        self.assertNotIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)

    def test_filtering_listing_with_category_read_only(self):
        """Test filtering a listing with a category"""
        category = Category.objects.create(name='Drums')
        c1 = create_listing(user=self.user)
        c2 = create_listing(user=self.user, title='Sample2')
        c2.category.add(category)
        s1 = ListingSerializer(c1)
        s2 = ListingSerializer(c2)
        params = {'category': f'{category.id}'}
        res = self.client.get(READ_LISTINGS_URL, params)
        self.assertNotIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)


class AdminPrivateTestCase(TestCase):
    """Tests that admin can access and edit all listings"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
                                email='test@example.com',
                                first_name='Joe',
                                last_name='Smith',
                                phone_number='8054394923',
                                password='testpass123')
        self.client.force_authenticate(self.user)


    def test_retrieve_listings(self):
        """Test retriving a list of listings shows all listings"""
        create_listing(user=self.user)
        new_user = create_user(email='new@example.com',
                               password='123455',
                               first_name='John',
                               last_name='Smith',
                               phone_number='2402345642')
        create_listing(user=new_user, title='Other User Listing')
        res = self.client.get(LISTINGS_URL)

        listings = Listing.objects.all().order_by('-id')
        serializer = ListingSerializer(listings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_admin_create_listing(self):
        """Test creating a listing as an admin success"""
        payload = {
            'title': 'sample listing',
            'price_cents': 10000,
            'description':'sample description',
            'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
        }
        res = self.client.post(LISTINGS_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        listing = Listing.objects.get(id=res.data['id'])
        for k, v in payload.items():
            if k == 'address':
                self.assertTrue(Address.objects.filter(address_1=payload['address']['address_1']).exists())
            else:
                self.assertEqual(getattr(listing, k), v)
        self.assertEqual(listing.user, self.user)

    def test_update_other_user_listing_success(self):
        """Test changing the listing user results in success"""
        new_user = create_user(email='new@example.com',
                               password='123455',
                               first_name='John',
                               last_name='Smith',
                               phone_number='2402345642')
        listing = create_listing(user=new_user)

        payload = {'title':'New title'}
        url = detail_url(listing.id)
        self.client.patch(url, payload)
        listing.refresh_from_db()
        self.assertIn(payload['title'], listing.title)

    def test_delete_other_user_listing_success(self):
        """Test trying to delete another user's listing gives error"""
        new_user = create_user(email='new@example.com',
                               password='123455',
                               first_name='John',
                               last_name='Smith',
                               phone_number='2402345642')
        listing = create_listing(user=new_user)

        url = detail_url(listing.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Listing.objects.filter(id=listing.id).exists())

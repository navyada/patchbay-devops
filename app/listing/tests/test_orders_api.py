"""
Tests for orders API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Listing,
    Orders,
    Address
    )
from listing.serializers import (
    OrdersSerializer
    )

ORDERS_URL = reverse('listing:orders-list')

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


class PublicCategoryAPITests(TestCase):
    """Test unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Make sure authentication is required to see orders"""
        res = self.client.get(ORDERS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateCategoryAPITests(TestCase):
    """Test authenticated API Requests"""
    def setUp(self):
            self.client = APIClient()
            self.user = create_user(email='test@example.com',
                                    first_name='Joe',
                                    last_name='Smith',
                                    phone_number='8054394923',
                                    password='testpass123')
            self.client.force_authenticate(self.user)

    def test_create_order(self):
        """Test creating orders"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054194923',
                            password='testpass123')
        listing = create_listing(user1)
        payload = {
            'user':self.user.id,
            'listing': listing.id,
            'requested_date':'2023-10-26',
            'start_date':'2023-10-27',
            'end_date':'2023-10-29'
            }
        res = self.client.post(ORDERS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_retrieve_order(self):
        """Test retrieving a user's orders"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054374923',
                            password='testpass123')
        listing = create_listing(user1)
        Orders.objects.create(user=self.user,
                                    lender=listing.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        res = self.client.get(ORDERS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_only_users_orders(self):
        """Test that other users orders are not returned"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054494923',
                            password='testpass123')
        listing = create_listing(user1)
        Orders.objects.create(user=self.user,
                                    lender=listing.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        user2 = create_user(email='test2@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054394933',
                            password='testpass123')
        Orders.objects.create(user=user2,
                                    lender=listing.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        res = self.client.get(ORDERS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(Orders.objects.count(), 2)

    def test_rental_and_lender_orders_retrived(self):
        """Test that both renter and lender order requests are retrieved"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054594923',
                            password='testpass123')
        listing = create_listing(user1)
        Orders.objects.create(user=self.user,
                                    lender=listing.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        listing = create_listing(self.user)
        Orders.objects.create(user=user1,
                                    lender=listing.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        res = self.client.get(ORDERS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_cannot_self_order(self):
        listing = create_listing(self.user)
        payload = {
            'user':self.user.id,
            'listing': listing.id,
            'requested_date':'2023-10-26',
            'start_date':'2023-10-27',
            'end_date':'2023-10-29'
            }
        res = self.client.post(ORDERS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_values_correct(self):
        """Test that lender id and subtotal_price are correct"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054194923',
                            password='testpass123')
        listing = create_listing(user1)
        payload = {
            'user':self.user.id,
            'listing': listing.id,
            'requested_date':'2023-10-26',
            'start_date':'2023-10-27',
            'end_date':'2023-10-29'
            }
        res = self.client.post(ORDERS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['lender'], user1.id)
        self.assertEqual(float(res.data['subtotal_price']), float(50200*2))

    def test_update_order(self):
        """Test that order and update time are updated"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054194923',
                            password='testpass123')
        listing = create_listing(user1)
        payload = {
            'user':self.user.id,
            'listing': listing.id,
            'requested_date':'2023-10-26',
            'start_date':'2023-10-27',
            'end_date':'2023-10-29'
            }
        res = self.client.post(ORDERS_URL, payload)
        payload = {
            'lender_response':'Approve',
            'status':'Approved'
        }
        url = reverse('listing:orders-detail', args=[res.data['id']])
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['status'], 'Approved')
        self.assertNotEqual(res.data['updated_at'], res.data['created_at'])

    def test_delete_order_error(self):
        """Test that users cannot delete an order"""
        """Test that order and update time are updated"""
        user1 = create_user(email='test1@example.com',
                            first_name='Joe',
                            last_name='Smith',
                            phone_number='8054194923',
                            password='testpass123')
        listing = create_listing(user1)
        payload = {
            'user':self.user.id,
            'listing': listing.id,
            'requested_date':'2023-10-26',
            'start_date':'2023-10-27',
            'end_date':'2023-10-29'
            }
        res = self.client.post(ORDERS_URL, payload)
        url = reverse('listing:orders-detail', args=[res.data['id']])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

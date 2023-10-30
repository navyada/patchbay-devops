"""
Test that users can write a review
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Listing,
    Address,
    ListingReview,
    UserReview,
    Orders
    )


REVIEW_URL = reverse('listing:listingreview-list')
READ_REVIEW_URL= reverse('listing:listingreviewreadonly-list')
USER_REVIEW_URL = reverse('listing:userreview-list')
READ_USER_REVIEW_URL = reverse('listing:userreviewreadonly-list')

def detail_url(id):
    """Create and return URL for detailed listing review"""
    return reverse('listing:listingreview-detail', args=[id])

def user_detail_url(id):
    """Create and return URL for detailed user review"""
    return reverse('listing:userreview-detail', args=[id])

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


### Tests for listing reviews ###
class PublicListingReviewApiTests(TestCase):
    """Test unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving saved listings"""
        res = self.client.get(READ_REVIEW_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

class PrivateListingReviewAPITests(TestCase):
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
        self.user1 = create_user(
                email='test123@example.com',
                password='testpass123',
                first_name='Jones',
                last_name='Martin',
                phone_number='8054929345'
                )
        self.listing = create_listing(user=self.user1)

    def test_create_review(self):
        """Test creating a review"""
        payload = {
            'user':self.user.id,
            'listing':self.listing.id,
            'stars':3,
            'text':'Review created'
        }
        res = self.client.post(REVIEW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_review(self):
        review = ListingReview.objects.create(user=self.user, listing=self.listing, stars=2, text='Old Review')
        payload = {'stars':3, 'text':'Improved review'}
        res = self.client.patch(detail_url(review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['stars'], 3)

    def test_delete_review(self):
        review = ListingReview.objects.create(user=self.user, listing=self.listing, stars=2, text='Old Review')
        res = self.client.delete(detail_url(review.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ListingReview.objects.count(), 0)

    def test_update_other_review_error(self):
        listing = create_listing(self.user)
        review = ListingReview.objects.create(user=self.user1, listing=listing, stars=2, text='Review')
        payload = {'stars':3, 'text':'Improved review'}
        res = self.client.patch(detail_url(review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ListingReview.objects.count(),1)

    def test_no_duplicate_reviews(self):
        """Test that a user can only make one review per listing"""
        review = ListingReview.objects.create(user=self.user, listing=self.listing, stars=2, text='Old Review')
        payload = {'user':self.user.id, 'listing':self.listing.id, 'stars':3, 'text':'New Review'}
        res = self.client.post(REVIEW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_write_review_self_listing_error(self):
        """Test that a user cannot write a review on their own listing"""
        listing = create_listing(self.user)
        payload = {'user':self.user.id, 'listing':listing.id, 'stars':5, 'text':'Greate product'}
        res = self.client.post(REVIEW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

### Tests for user reviews ###

class PublicListingReviewApiTests(TestCase):
    """Test unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for retrieving saved listings"""
        res = self.client.get(READ_USER_REVIEW_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

class PrivateUserReviewAPITests(TestCase):
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
        self.user1 = create_user(
                email='test123@example.com',
                password='testpass123',
                first_name='Jones',
                last_name='Martin',
                phone_number='8054929345'
                )
        self.listing = create_listing(user=self.user)

    def test_create_review(self):
        """Test creating a review"""
        default = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description',
        'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
                 }
        address = default.pop('address', None)
        address, created = Address.objects.get_or_create(**address)
        listing = Listing.objects.create(user=self.user, address=address, **default)
        user2 = get_user_model().objects.create_user(
                email='test1233@example.com',
                password='password123',
                first_name='Homer',
                last_name='Simpson',
                phone_number='8054999345')
        order = Orders.objects.create(user=user2,
                                      lender=self.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        payload = {
            'lender':self.user.id,
            'renter':user2.id,
            'stars':3,
            'text':'Review created'
        }
        res = self.client.post(USER_REVIEW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_review(self):
        review = UserReview.objects.create(lender=self.user, renter=self.user1, stars=2, text='Old Review')
        payload = {'stars':3, 'text':'Improved review'}
        res = self.client.patch(user_detail_url(review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['stars'], 3)

    def test_delete_review(self):
        review = UserReview.objects.create(lender=self.user, renter=self.user1, stars=2, text='Old Review')
        res = self.client.delete(user_detail_url(review.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserReview.objects.count(), 0)

    def test_update_other_review_error(self):
        review = UserReview.objects.create(lender=self.user1, renter=self.user, stars=2, text='Review')
        payload = {'stars':3, 'text':'Improved review'}
        res = self.client.patch(user_detail_url(review.id), payload)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserReview.objects.count(),1)

    def test_no_duplicate_reviews(self):
        """Test that a lender can only make one review per user"""
        """Test creating a review"""
        default = {
        'title': 'Sample Title',
        'price_cents': 50200,
        'description': 'Sample Description',
        'address': {'address_1':'1197 W 36th St', 'city':'Los Angeles', 'state':'CA', 'zip_code':'90007'}
                 }
        address = default.pop('address', None)
        address, created = Address.objects.get_or_create(**address)
        listing = Listing.objects.create(user=self.user, address=address, **default)
        user2 = get_user_model().objects.create_user(
                email='test1233@example.com',
                password='password123',
                first_name='Homer',
                last_name='Simpson',
                phone_number='8054999345')
        order = Orders.objects.create(user=user2,
                                      lender=self.user,
                                    listing=listing,
                                    requested_date='2023-10-26',
                                    start_date='2023-10-27',
                                    end_date='2023-10-29')
        review = UserReview.objects.create(lender=self.user, renter=user2, stars=2, text='Old Review')
        payload = {'lender':self.user.id, 'renter':user2.id, 'stars':3, 'text':'New Review'}
        res = self.client.post(USER_REVIEW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


"""
Database models
"""

from django.db import models
from django.contrib.auth.models import (
                                        AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin
                                        )
from django.conf import settings
import uuid
import os
from django.core.exceptions import ValidationError

from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import ugettext as _
from localflavor.us.models import USStateField
from datetime import date
from typing import Union

def listing_image_file_path(instance, filename):
    """Generate file path for new listing image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4}{ext}'

    return os.path.join('uploads', 'listing', filename)

def user_image_file_path(instance, filename):
    """Generate file path for new user image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4}{ext}'

    return os.path.join('uploads', 'user', filename)

class UserManager(BaseUserManager):
    """" Manager for users"""
    def create_user(self, email, first_name,
                    last_name, phone_number, password=None, **extra_fields):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        if not first_name:
            raise ValueError('User must add a first name.')
        if not last_name:
            raise ValueError('User must add a last name.')
        if not phone_number:
            raise ValueError('User must have a phone number.')

        # Check if the email or phone number already exists in the database
        if self.model.objects.filter(email=email).exists():
            raise ValidationError('Email is already in use.')
        if self.model.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('Phone number is already in use.')

        user = self.model(
                        email=self.normalize_email(email),
                        first_name=first_name,
                        last_name=last_name,
                        phone_number=phone_number,
                        **extra_fields
                        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, first_name,
                        last_name, phone_number, password, **extra_fields
                        ):
        """Create and return a new superuser"""
        user = self.create_user(email, first_name,
                                last_name, phone_number, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_lender = models.BooleanField(default=False)
    city = models.CharField(max_length=255, null=True)
    bio = models.TextField(max_length=500, null=True)
    studio = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    last_login = models.DateTimeField(null=True)
    email_validated = models.BooleanField(default=False)
    phone_validated = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']


class UserImage(models.Model):
    """User images"""
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(null=True, upload_to=user_image_file_path)

class Address(models.Model):
    address_1 = models.CharField(_("address"), max_length=128)
    address_2 = models.CharField(_("address cont'd"), max_length=128, blank=True)

    city = models.CharField(_("city"), max_length=64, default="Los Angeles")
    state = USStateField(_("state"), default="CA")
    zip_code = models.CharField(_("zip code"), max_length=5, default="90007")


class UnavailableDate(models.Model):
    """Model to store unavailable dates for listings"""
    date = models.DateField()
    # class Meta:
        # unique_together = ('date',)
    def clean(self):
        """
        Custom validation to ensure that unavailable dates are not in the past.
        """
        if self.date < date.today():
            raise ValidationError(_('Unavailable date cannot be in the past.'))
    def __str__(self):
        return str(self.date)

class Category(models.Model):
    """ Category for filtering instruments"""
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='child_categories'
    )
    def __str__(self):
        return self.name

class Listing(models.Model):
    """Listing object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    title=models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price_cents=models.PositiveIntegerField()
    year = models.PositiveIntegerField(null=True)
    make = models.CharField(max_length=255, null=True)
    model = models.CharField(max_length=255, null=True)
    replacement_value_cents = models.PositiveIntegerField(null=True)
    category = models.ManyToManyField('Category')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    unavailable_dates = models.ManyToManyField('UnavailableDate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)

    @property
    def avg_stars(self) -> Union[float, int]:
        reviews = self.listingreview_set.all()
        if reviews:
            total_stars = sum(review.stars for review in reviews)
            return total_stars / len(reviews)
        else:
            return 0

    @property
    def num_reviews(self)-> Union[float, int]:
        reviews = self.listingreview_set.all()
        if reviews:
            return len(reviews)
        else:
            return 0
    def __str__(self):
        return self.title

class ListingImage(models.Model):
    """Listing images"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='image')
    image = models.ImageField(null=True, upload_to=listing_image_file_path)
    order = models.IntegerField(default=1)




class Saved(models.Model):
    """Save a listing"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'listing')

class ListingReview(models.Model):
    """Write or see a review for a listing"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    stars = models.IntegerField(default=0)
    text = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'listing')


ORDER_STATUS_PENDING = 'Pending'
ORDER_STATUS_APPROVED = 'Approved'
ORDER_STATUS_DENIED = 'Denied'
ORDER_STATUS_CANCELLED = 'Cancelled'
ORDER_STATUS_CHOICES = [
    (ORDER_STATUS_PENDING, 'Pending'),
    (ORDER_STATUS_APPROVED, 'Approved'),
    (ORDER_STATUS_DENIED, 'Denied'),
    (ORDER_STATUS_CANCELLED, 'Cancelled')
]

LENDER_RESPONSE_APPROVE = 'Approve'
LENDER_RESPONSE_DENY = 'Deny'
LENDER_RESPONSE_CHOICES = [
    (LENDER_RESPONSE_APPROVE, 'Approve'),
    (LENDER_RESPONSE_DENY, 'Deny')]
class Orders(models.Model):
    """Create or update an order"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lender_orders', null=True)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name='orders')
    requested_date = models.DateField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default=ORDER_STATUS_PENDING)
    lender_response = models.CharField(max_length=20, choices=LENDER_RESPONSE_CHOICES, null=True, blank=True)
    subtotal_price = models.PositiveIntegerField( null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserReview(models.Model):
    """Write or see a review for a renter"""
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lender_review')
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='renter_review')
    stars = models.IntegerField(default=0)
    text = models.TextField(max_length=500, blank=True)
    class Meta:
        unique_together = ('lender', 'renter')




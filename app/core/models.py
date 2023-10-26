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


class Address(models.Model):
    address_1 = models.CharField(_("address"), max_length=128)
    address_2 = models.CharField(_("address cont'd"), max_length=128, blank=True)

    city = models.CharField(_("city"), max_length=64, default="Los Angeles")
    state = USStateField(_("state"), default="CA")
    zip_code = models.CharField(_("zip code"), max_length=5, default="90007")


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
    replacement_value = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    category = models.ManyToManyField('Category', blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    # image = models.ImageField(null=True, upload_to = recipe_image_file_path)
    def __str__(self):
        return self.title

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
    class Meta:
        unique_together = ('user', 'listing')


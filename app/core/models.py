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
                        last_name, phone_number, password
                        ):
        """Create and return a new superuser"""
        user = self.create_user(email, first_name,
                                last_name, phone_number, password)
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

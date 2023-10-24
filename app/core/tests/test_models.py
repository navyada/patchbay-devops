""" Test our models"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch
from core import models

from django.core.exceptions import ValidationError


def create_user(email='user@example.com', password='password'):
    """create and return a new user"""
    return get_user_model().objects.create_user(
        email=email,
        password=password)


class ModelTests(TestCase):
    """Test the models"""

    testemail = 'test@example.com'
    testfirstname = 'Joe'
    testlastname = 'Smith'
    testphonenumber = '1233454567'
    testpassword = 'testpassword123'

    def test_create_user_with_email_successful(self):
        email = 'test@example.com'
        password = 'testpass123'
        first_name = 'Joe'
        last_name = 'Smith'
        phone_number = '1234567890'
        user = get_user_model().objects.create_user(
            email,
            first_name,
            last_name,
            phone_number,
            password
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.phone_number, phone_number)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test email is normalized for new users"""
        samples_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        i = 0
        for email, expected in samples_emails:
            phone_number = '123456789' + str(i)
            user = get_user_model().objects.create_user(
                email=email,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number=phone_number)
            self.assertEqual(user.email, expected)
            i += 1

    def test_new_user_without_email_raises_error(self):
        """ Test that creating a user without email raises an exception"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number=self.testphonenumber)

    def test_new_user_without_first_name_raises_error(self):
        """ Test that creating a user without first name raises an exception"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=self.testemail,
                password=self.testpassword,
                first_name='',
                last_name=self.testlastname,
                phone_number=self.testphonenumber)

    def test_new_user_without_last_name_raises_error(self):
        """ Test that creating a user without last name raises an exception"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=self.testemail,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name='',
                phone_number=self.testphonenumber)

    def test_new_user_without_phone_number_raises_error(self):
        """ Test that creating a user without
        phone number raises an exception"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=self.testemail,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number='')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
                email=self.testemail,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number=self.testphonenumber
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_user_with_additional_fields(self):
        """Test creating a user with optional fields"""
        user = get_user_model().objects.create_user(
                email=self.testemail,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number=self.testphonenumber,
                bio='Hola! I\'m Joe!',
                studio='Best Music Studios')
        self.assertEqual(user.bio, 'Hola! I\'m Joe!')
        self.assertEqual(user.studio, 'Best Music Studios')

    def test_create_user_with_taken_email_raises_error(self):
        """Test that creating a user with an email
          that's already used creates an error"""
        get_user_model().objects.create_user(
                email=self.testemail,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number=self.testphonenumber,
               )
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                    email=self.testemail,
                    password=self.testpassword,
                    first_name=self.testfirstname,
                    last_name=self.testlastname,
                    phone_number='0987654321')

    def test_create_user_with_taken_phone_number_raises_error(self):
        """Test that creating a user with a phone number
          that's already used creates an error"""
        get_user_model().objects.create_user(
                email=self.testemail,
                password=self.testpassword,
                first_name=self.testfirstname,
                last_name=self.testlastname,
                phone_number=self.testphonenumber,
               )
        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                    email='user1@example.com',
                    password=self.testpassword,
                    first_name=self.testfirstname,
                    last_name=self.testlastname,
                    phone_number=self.testphonenumber)

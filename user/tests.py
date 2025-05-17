from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import User


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.existing_user = User.objects.create_user(
            username="bla1",
            first_name="bla",
            last_name="bla",
            email="bla1@example.com",
            national_id="0987654321",
            user_type="student",
            password="bla",
        )

    def test_user_registration_success(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "bla@example.com",
                "national_id": "1234567890",
                "user_type": "student",
                "password": "bla",
                "confirm_password": "bla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)  # Including the existing user
        self.assertEqual(User.objects.get(username="bla").email, "bla@example.com")

    def test_user_registration_with_mismatched_passwords(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "bla@example.com",
                "national_id": "1234567890",
                "user_type": "student",
                "password": "bla",
                "confirm_password": "blabla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_registration_with_invalid_national_id(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "bla@example.com",
                "national_id": "12345",
                "user_type": "student",
                "password": "bla",
                "confirm_password": "bla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_registration_with_duplicate_email(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "bla1@example.com",  # Duplicate email
                "national_id": "1234567890",
                "user_type": "student",
                "password": "bla",
                "confirm_password": "bla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_registration_with_duplicate_national_id(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "bla@example.com",
                "national_id": "0987654321",  # Duplicate national ID
                "user_type": "student",
                "password": "bla",
                "confirm_password": "bla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_registration_with_missing_required_fields(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "",
                "national_id": "",
                "user_type": "",
                "password": "bla",
                "confirm_password": "bla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_user_registration_with_invalid_user_type(self):
        response = self.client.post(
            "/user/register/",
            {
                "username": "bla",
                "first_name": "bla",
                "last_name": "bla",
                "email": "bla@example.com",
                "national_id": "1234567890",
                "user_type": "bla",
                "password": "bla",
                "confirm_password": "bla",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

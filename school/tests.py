from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from user.models import *

from .models import *
from .permission import *
from .serializer import *


class SchoolViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()

        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpassword123",
            user_type="manager",
            national_id="0000000001",
        )
        self.manager_user = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="managerpassword123",
            user_type="manager",
            national_id="0000000002",
        )
        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="studentpassword123",
            user_type="student",
            national_id="0000000003",
        )
        self.teacher_user = User.objects.create_user(
            username="teacher",
            email="teacher@example.com",
            password="teacherpassword123",
            user_type="teacher",
            national_id="0000000004",
        )

        self.school = School.objects.create(
            name="Test School", manager=self.manager_user
        )

    def test_create_school_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "New School",
            "manager": self.manager_user.id,
        }

        response = self.client.post("/schools/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(School.objects.filter(name="New School").exists())

    def test_create_school_by_non_admin(self):
        self.client.force_authenticate(user=self.manager_user)
        url = reverse("school-list")
        data = {
            "name": "New School",
            "manager": self.manager_user.id,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_school_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("school-detail", kwargs={"pk": self.school.pk})
        data = {
            "name": "Updated School",
            "manager": self.manager_user.id,
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(School.objects.get(pk=self.school.pk).name, "Updated School")

    def test_delete_school_by_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("school-detail", kwargs={"pk": self.school.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(School.objects.filter(pk=self.school.pk).exists())

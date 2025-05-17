from django.contrib.auth.models import AbstractUser
from django.db import models

from .usermanager import UserManager


class User(AbstractUser):
    USER_TYPES = (
        ("manager", "Manager"),
        ("teacher", "Teacher"),
        ("student", "Student"),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    national_id = models.CharField(
        unique=True,
        null=False,
        max_length=10,
        help_text="10-digit national id",
    )
    objects = UserManager()

    def __str__(self):
        return f"{self.username} - {self.bio}"

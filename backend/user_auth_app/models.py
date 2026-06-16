from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with optional birthdate and address fields."""

    birthdate = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username

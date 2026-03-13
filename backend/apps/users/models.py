from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with additional fields."""

    email = models.EmailField(unique=True)
    organization = models.CharField(max_length=255, blank=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ('admin', 'Administrator'),
            ('analyst', 'Analyst'),
            ('viewer', 'Viewer'),
        ],
        default='analyst',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

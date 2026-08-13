from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None

    ROLE_CHOICES = [
        ('OWNER', 'Property Owner'),
        ('TENANT', 'Tenant'),
        ('ADMIN', 'Administrator'),
    ]

    ACCOUNT_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual'),
        ('ORGANIZATION', 'Organization / Real Estate Office'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='TENANT'
    )
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='INDIVIDUAL'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone']

    def __str__(self):
        return self.email
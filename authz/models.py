from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLE_CHOICES = (
        ('undefine', 'Undefine'),
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='undefine')
    phone = models.CharField(max_length=15, blank=True, default="")
    avatar = models.ImageField(upload_to="user/profiles", blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
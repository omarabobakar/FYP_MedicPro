from django.db import models
from authz.models import User
# Create your models here.
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    medical_history = models.TextField()
    date_of_birth = models.DateField(blank=True, null=True)
    GANDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('private', 'Private'),
    )
    gander = models.CharField(max_length=10, choices=GANDER_CHOICES, default='private')
    def __str__(self):
        return f"{self.user.username}"
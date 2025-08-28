from django.db import models
from authz.models import User
import uuid

# Create your models here.
class Specialization(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.ManyToManyField(Specialization, related_name="specializations")
    qualifications = models.TextField(blank=True, null=True)
    available_times = models.CharField(max_length=100, blank=True)
    clinic_address = models.CharField(max_length=200, blank=True)
    profile_completed = models.BooleanField(default=False)
    consultation_fee = models.CharField(default=0.0,max_length=10, blank=True)
    pmdc_number = models.CharField(max_length=7, unique=True, editable=False)
    
    def __str__(self):
        return f"{self.user.username}"

    
    def generate_unique_pmdc_number(self):
        while True:
            pmdc_number = str(uuid.uuid4().int)[:7]
            if not Doctor.objects.filter(pmdc_number=pmdc_number).exists():
                return pmdc_number

    def save(self, *args, **kwargs):
        if not self.pmdc_number:
            self.pmdc_number = self.generate_unique_pmdc_number()
        super().save(*args, **kwargs)
from django.db import models
from doctor.models import *
from patient.models import *

from datetime import datetime, timedelta

class Appointment(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    time = models.TimeField()
    day = models.CharField(max_length=20)
    date = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self) -> str:
        return f"Id - {self.id} Dr. {self.doctor} Date - {self.date} Time - {self.time} Status - {self.status}"

    def save(self, *args, **kwargs):
        
        weekdays = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        try:

            today = datetime.now()
            
            current_weekday = today.weekday()
            
            target_weekday = weekdays[self.day]
            
            days_until_next = (target_weekday - current_weekday + 7) % 7
            if days_until_next == 0:
                days_until_next = 7
            self.date = today.date() + timedelta(days=days_until_next)
            super().save(*args, **kwargs)
        except Exception as e:
            super().save(*args, **kwargs)
            print(e)
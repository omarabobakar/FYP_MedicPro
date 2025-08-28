
from django.urls import path
from .views import *
urlpatterns = [
    path("doctor_dashboard", doctorDashboard, name="doctor_dashboard" ),
    path("update_doctor_profile", updateDoctorProfile, name="update_doctor_profile" ),
    path("doctor_profile/<str:username>", showDoctorProfileToPatient, name="doctor_profile"),
    path("schedule_appointment", scheduleAppointmentWithDoctor, name="schedule_appointment"),
    
]
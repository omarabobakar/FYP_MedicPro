
from django.urls import path
from .views import *
urlpatterns = [
    path("patient_dashboard", patientDashboard, name="patient_dashboard" ),
    path("update_patient_profile",updatePatientProfile,name="update_patient_profile"),
    path("appointment_details/<int:id>", checkAppointment, name="appointment_details"),
    path("cancel_appointment/<int:id>", cancelAppointment, name="cancel_appointment"),
    path("complete_appointment/<int:id>", completeAppointment, name="complete_appointment")
]
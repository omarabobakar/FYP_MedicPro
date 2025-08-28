from django.shortcuts import render, redirect
from .models import *
from home.models import *
from doctor.models import *
from authz.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from medic_pro.email_views import send_appointment_mail
from datetime import datetime

# Create your views here.

@login_required
def patientDashboard(request):
    if request.user.role != "patient":
        messages.error(request,"You can't access patient Dashboard")
        return redirect('home')
    patient = Patient.objects.get(user=request.user)
    appointments = Appointment.objects.filter(patient=patient)
    cancelled_appointments = None
    pending_appointments = None
    if appointments:
        cancelled_appointments = appointments.filter(status="cancelled")
        pending_appointments = appointments.filter(status="scheduled")

    doctors = Doctor.objects.all()
    context = {
        'patient': patient,
        'appointments': appointments,
        'doctors': doctors,
        "cancelled_appointments":cancelled_appointments,
        "pending_appointments":pending_appointments
    }
    return render(request, "dashboard/patientDashboard.html", context)


@login_required
@csrf_exempt
def updatePatientProfile(request):
    patient = Patient.objects.get(user=request.user)
    user = request.user
    if request.user.role != "patient":
        messages.error(request,"You can't access patient Dashboard")
        return redirect('home')
    
    if request.method == "POST":
        patient.gander = request.POST.get('gander')
        date_of_birth_str = request.POST.get('birthday')
        if date_of_birth_str:
            patient.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
        else:
            patient.date_of_birth = None
        patient.medical_history = request.POST.get('medicalRecord')
        patient.save()
        messages.info(request, "Patient Record Updated")

        email = request.POST.get('email')
        username = request.POST.get('username')
        existing_email_user = User.objects.filter(email=email).exclude(pk=request.user.pk).exists()
        existing_username_user = User.objects.filter(username=username).exclude(pk=request.user.pk).exists()  
        if existing_email_user:
            messages.error(request, "Email is already in use.")
            return redirect('update_patient_profile')
        elif existing_username_user:
            messages.error(request, "Username is already in use.")
            return redirect('update_patient_profile')

        user.email = email
        user.phone = request.POST.get('phone')
        user.username = username
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        newAvatar = request.FILES.get('newAvatar')
        if newAvatar:
            user.avatar = newAvatar
        user.save()
        messages.success(request, "Personal Information Updated Successfully")

    context = {
        'patient': patient,
    }
    return render (request, "dashboard/patientProfileUpdate.html", context)


@login_required
def checkAppointment(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
        if appointment:
            context = {
                'appointment': appointment
            }
            return render(request,"pages/appointmentDetails.html", context)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found!")
        return redirect('home')
    

@login_required
def cancelAppointment(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
        if appointment.patient.user == request.user or appointment.doctor.user == request.user:
            email_sent = send_appointment_mail(appointment, 'cancelled')
            if email_sent:
                appointment.status = "cancelled"
                appointment.save()
                messages.warning(request, "Appointment Cancelled Successfully")
            else:
                messages.error(request, "Failed to Cancell Appointment. Please check your internet connection.")
            return redirect('appointment_details', id=appointment.id)
        else:
            messages.error(request, "You can't cancel this appointment")
            return redirect("home")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found!")
        return redirect('home')
    
@login_required
def completeAppointment(request, id):
    try:
        appointment = Appointment.objects.get(id=id)
        if appointment.patient.user == request.user or appointment.doctor.user == request.user:
            email_sent = send_appointment_mail(appointment, 'completed')
            if email_sent:
                appointment.status = "completed"
                appointment.save()
                messages.warning(request, "Appointment marked as Completed Successfully")
            else:
                messages.error(request, "Failed to mark appointment as completed. Please check your internet connection.")
            
            return redirect('appointment_details', id=appointment.id)
        else:
            messages.error(request, "You can't change this appointment")
            return redirect("home")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found!")
        return redirect('home')
    

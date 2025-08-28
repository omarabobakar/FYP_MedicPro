from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import *
from authz.models import *
from patient.models import *
from home.models import *
import json
from medic_pro.email_views import send_appointment_mail
from medic_pro.Ai_Tasks import is_time_between_7am_and_9pm, is_doctor_available, convert_to_12_hour
# Create your views here.

@login_required
def doctorDashboard(request):
    doctor = Doctor.objects.get(user=request.user)
    appointments = Appointment.objects.filter(doctor__user = request.user)
    cancelled_appointments = None
    pending_appointments = None
    if appointments:
        cancelled_appointments = appointments.filter(status="cancelled")
        pending_appointments = appointments.filter(status="scheduled")
    specializations = doctor.specialization.all()
    context = {
        "doctor":doctor,
        "specializations":specializations,
        "appointments": appointments,
        "cancelled_appointments": cancelled_appointments,
        "pending_appointments": pending_appointments,
    }
    return render(request, 'dashboard/doctorDashboard.html', context)


@login_required
@csrf_exempt
def updateDoctorProfile(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
        specialization = Specialization.objects.all()
        user = request.user
        if request.user.role != "doctor":
            messages.error(request,"You can't access Doctor Dashboard")
            return redirect('home')
        if request.method == "POST":
            selected_days = request.POST.getlist('selected_days[]')
            selected_specs = request.POST.getlist('selected_specs[]')
            doctor.specialization.clear()
            for spec in selected_specs:
                specObj = Specialization.objects.get(name=spec)
                if specObj:
                    doctor.specialization.add(specObj)
            doctor.available_times = ','.join(selected_days)
            doctor.qualifications = request.POST.get("qualifications")
            doctor.clinic_address = request.POST.get("clinic_address")
            doctor.consultation_fee = request.POST.get("fee")
            if doctor.available_times == "" or doctor.specialization.count() == 0:
                doctor.profile_completed = False
            else:
                doctor.profile_completed = True
            doctor.save()

            email = request.POST.get('email')
            username = request.POST.get('username')
            existing_email_user = User.objects.filter(email=email).exclude(pk=user.pk).exists()
            existing_username_user = User.objects.filter(username=username).exclude(pk=user.pk).exists()  
            if existing_email_user:
                messages.error(request, "Email is already in use.")
                return redirect('update_doctor_profile')
            elif existing_username_user:
                messages.error(request, "Username is already in use.")
                return redirect('update_doctor_profile')

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
            'doctor': doctor,
            'specializations':specialization
        }
        return render (request, "dashboard/doctorProfileUpdate.html", context)
    except Exception as e:
        print(e)
        messages.warning(request, "Something Went Wrong")
        return redirect('home')


from datetime import time, timedelta, datetime

def get_busy_slots(appointments):
    time_slots = []
    for appointment in appointments:
        # Extract time and day from the appointment
        t = appointment.time
        day = appointment.day
        base_time = datetime.combine(datetime.today(), t)
        start_time = (base_time - timedelta(minutes=30)).time()
        end_time = (base_time + timedelta(minutes=30)).time()
        start_time_str = start_time.strftime('%I:%M %p')
        end_time_str = end_time.strftime('%I:%M %p')
        time_slot = f"{day}: {start_time_str} to {end_time_str}"
        time_slots.append(time_slot)
    return time_slots


@login_required
def showDoctorProfileToPatient(request,username):
    doctor = Doctor.objects.get(user__username = username)
    available_days = doctor.available_times.split(",") if doctor.available_times else []
    booked_appointments = Appointment.objects.filter(doctor=doctor, status='scheduled')
    busy_time = []
    if booked_appointments:
        busy_time = get_busy_slots(booked_appointments)
        
    context = {
        'doctor':doctor,
        'available_days':available_days,
        'busy_times':busy_time,
        
        }
    return render(request, "dashboard/doctorProfile.html", context)


@login_required
@csrf_exempt
def scheduleAppointmentWithDoctor(request):
    if request.user.is_superuser:
        messages.warning(request, "Admin Can't Schedule an Appointment.")
        return redirect('admin_dashboard')
    if request.method == "POST":
        try:
            patient = Patient.objects.get(user=request.user)
            doctor_username = request.POST.get("doctor")
            doctor = Doctor.objects.get(user__username=doctor_username)
        except Patient.DoesNotExist:
            messages.error(request, "Patient not found.")
            return redirect("doctor_profile", username=request.user.username)
        except Doctor.DoesNotExist:
            messages.error(request, "Doctor not found.")
            return redirect("doctor_profile", username=request.user.username)
        
        day = request.POST.get("day")
        time = request.POST.get("time")
        note = request.POST.get("note")
        
        if not time or day == "Choose Day":
            messages.error(request, "Please choose a day and time.")
            return redirect("doctor_profile", username=doctor_username)
        
        if not is_time_between_7am_and_9pm(time):
            messages.error(request, "Choose time between 7:00 Am to 9:00 Pm")
            return redirect("doctor_profile", username=doctor_username)
        
        if not is_doctor_available(doctor, time, day):
            messages.error(request, "This Doctor is not available at this time. Please choose another day/time or doctor")
            return redirect("doctor_profile", username=doctor_username)

        newAppointment = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            day=day,
            time=time,
            note=note
        )
        email_sent = send_appointment_mail(newAppointment, 'scheduled')
        if email_sent:
            newAppointment.save()
            messages.success(request, "Your appointment has been fixed.")
        else:
            newAppointment.delete()
            messages.error(request, "Failed to Book Appointment. Please Check your internet Connection")
        return redirect("doctor_profile", username=doctor_username)
    return redirect("home") 
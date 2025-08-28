from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import *
from authz.models import *
from doctor.models import *
from patient.models import *
from medic_pro.Gemini_Ai import get_ai_response
from django.http import JsonResponse
from medic_pro.Ai_Tasks import *

from medic_pro.appointment_instructions import SHOW_APPOINTMENTS_TABLES_TO_USER
import re
import datetime
from medic_pro.email_views import send_appointment_mail
# Create your views here.

def index(request):
    return render(request, 'home/index.html')

def about(request):
    return render(request, 'home/about.html')

def contact(request):
    return render(request, 'home/contact.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "You can't Acess the Admin Panel")
        return redirect("home")
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    appointments = Appointment.objects.all()
    
    specializations = Specialization.objects.all()
    cancelled_appointments = None
    pending_appointments = None
    if appointments:
        cancelled_appointments = appointments.filter(status='cancelled')
        pending_appointments = appointments.filter(status="scheduled")

    context = {
        'doctors':doctors,
        'patients':patients,
        'appointments':appointments,
        'cancelled_appointments':cancelled_appointments,
        'pending_appointments':pending_appointments,
        
        'specializations':specializations,

    }
    return render(request, 'dashboard/adminDashboard.html',context)


@login_required
@csrf_exempt
def update_admin_profile(request):
    if request.method == 'POST':
        user = request.user
        email = request.POST.get('email')
        username = request.POST.get('username')
        existing_email_user = User.objects.filter(email=email).exclude(pk=request.user.pk).exists()
        existing_username_user = User.objects.filter(username=username).exclude(pk=request.user.pk).exists()  
        if existing_email_user:
            messages.error(request, "Email is already in use.")
            return redirect('update_admin_profile')
        elif existing_username_user:
            messages.error(request, "Username is already in use.")
            return redirect('update_admin_profile')

        user.email = email
        user.username = username
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        newAvatar = request.FILES.get('newAvatar')
        if newAvatar:
            user.avatar = newAvatar
        user.save()
        messages.success(request, "Personal Information Updated Successfully")
    return render(request, "dashboard/adminProfileUpdate.html")




@login_required
@csrf_exempt
def chat_bot(request):
    if request.user.role != "patient":
        messages.error(request, "Only patient can use Chat-Bot")
        return redirect('home')
    if request.method == 'POST':
        query = request.POST.get("query")
        print(query)
        if not query:
            return JsonResponse({"error": "Please Enter Query"}, status=400)
        if query == "":
            messages.error(request, "Please Enter Query")
        try:
            response = get_ai_response(query)
        except Exception as e:
            print(e)
            response = "Sorry I am not able to understand your query"
        response = response.replace("* ","<br>")
        response = response.replace("*","")
        if "check_appointment_details" in response:
            doctor, day, time  = extract_appointment_details(response.replace("<br>", "\n"))
            day = day.lower()
            day = day.capitalize()
            print("*"*20)
            print(day)
            print("*"*20)

            try:
                doctorUser = doctor.replace("Dr. ","").lower()
                doctorUser = re.sub(r'[^a-zA-Z0-9]', '', doctorUser)
                find_doctor_name = User.objects.get(username=doctorUser)
                if find_doctor_name:
                    doctor_name = find_doctor_name.username
                    patient_name = request.user.username
                    appointment = book_appointment_with_chatbot(patient_name, doctor_name, day, time)
                    if appointment:
                        response = appointment
                    else:
                        response = "Sorry, Unable to Book Appointment"
                else:
                    print("Dr. couldn't found with ",doctor.replace("Dr. ","").lower())
            except Exception as e:
                print(e)
                response = "Failed to book appointment please try again."
        
        elif "give_me_user_appointments" in response:
            appointments = Appointment.objects.filter(patient__user=request.user)
            if appointments:
                print("Sending Appointments to Ai")
                response = get_ai_response(f"Instruction (must follow):\n {SHOW_APPOINTMENTS_TABLES_TO_USER} \n Appointments Data:\n {appointments}")
                try:
                    response = response.replace('```html\n', '').replace('\n```', '')
                except Exception as e:
                    print(e)
            else:
                response = "You haven't booked any appointment"
        
        if "appointment_cancelled" in response or "appointment_completed" in response:
            print("Try to cancel or complete appointment")
            try:
                app_id = extract_appointment_id(response)
                target_appointment = Appointment.objects.get(id=app_id)
                if target_appointment:
                    if target_appointment.patient.user == request.user:
                        if "appointment_cancelled" in response:
                            if target_appointment.status == 'completed':
                                response = "Can't Cancel the Completed Appointment"
                            elif target_appointment.status != "cancelled":
                                email_sent = send_appointment_mail(target_appointment, 'cancelled')
                                if email_sent:
                                    target_appointment.status = "cancelled"
                                    target_appointment.save()
                                    response = "Appointment Cancelled Successfully"
                                else:
                                    print("failed to send cancel appointment mail")
                                    response = "Failed to cancel appointment"
                            else:
                                response = "Failled to Cancel Appointment"
                        if "appointment_completed" in response:
                            if target_appointment.status == 'Cancelled':
                                response = "Can't Complete the cancelled Appointment"
                            elif target_appointment.status != "Completed":
                                email_sent = send_appointment_mail(target_appointment, 'completed')
                                if email_sent:
                                    target_appointment.status = "completed"
                                    target_appointment.save()
                                    response = "Appointment Completed Successfully"
                                else:
                                    print("failed to send complete appointment mail")
                                    response = "Failed to complete appointment"
                            else:
                                response = "Failed to Complete Appointment"
                    else:
                        response = "You are not authorized to update this appointment"
                else:
                    response = "Appointment Not Found"
            except Exception as e:
                print(e)
                response = e
        print(response)
        return JsonResponse({"response":response})
    return render(request, "chat/chatbot.html")




@login_required
@csrf_exempt
def add_new_spec(request):
    if request.method == "POST":
        if not request.user.is_superuser:
            messages.error(request, "Only Admin can Add new Specializations")
            return redirect("home")
        newSpec = request.POST.get("newSpec")
        new_spec_added = Specialization.objects.create(name=newSpec)
        if new_spec_added:
            messages.success(request, "Specialization Added Successfully")
            return redirect("admin_dashboard")
        try:
            pass
        except Exception as e:
            print(e)
            return redirect("admin_dashboard")
    else:
        messages.error(request, "Something went wrong")
        return redirect('home')


@login_required
def delete_spec(request, id):
    if not request.user.is_superuser:
        messages.error(request, "Only Admin can Delete Specializations")
        return redirect("home")
    try:
        targetSpec = Specialization.objects.get(pk=id)
        targetSpec.delete()
        messages.warning(request, "Specialization deleted successfully")
        return redirect("admin_dashboard")
    except Exception as e:
        print(e)
        messages.error(request, "Something Went Wrong")
        return redirect("home")
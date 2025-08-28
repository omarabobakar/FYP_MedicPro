from doctor.models import Doctor, Specialization
import re
from authz.models import User
from doctor.models import *
from patient.models import *
from home.models import *
from medic_pro.email_views import send_appointment_mail


def find_doctors_by_specialization(specialization_name):
    try:
        specialization = Specialization.objects.get(name=specialization_name)
        doctors = Doctor.objects.filter(specialization=specialization)
        if doctors:
            formatted_data = ""
            for doctor in doctors:
                formatted_data += f"<br>Name: {doctor.user.username}<br>"
                formatted_data += f"Specialization: {', '.join([spec.name for spec in doctor.specialization.all()])}<br>"
                formatted_data += f"Email: {doctor.user.email}<br>"
                formatted_data += f"Available Times: {doctor.available_times}<br>"
                formatted_data += f"Fee: {doctor.consultation_fee} <br>"
                formatted_data += f"Clinic Address: {doctor.clinic_address}<br>"
                formatted_data += f"Profile Url:http://127.0.0.1:8000/doctor/doctor_profile/{doctor.user.username}"
            return formatted_data, True
        else:
            return f"No doctors found for specialization: {specialization_name}", False
    except Specialization.DoesNotExist:
        return f"Specialization '{specialization_name}' does not exist.", False

import datetime

def convert_to_12_hour(time_str):
    time_str = str(time_str)
    time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S')
    return time_obj.strftime('%I:%M %p').lower()

def extract_appointment_details(text):
    """
    Extracts selected doctor, available day, and appointment time from the given text.
    """
    try:
        selected_doctor = re.search(r'selected_doctor:\s*(.*)', text).group(1).strip()
        available_day = re.search(r'available_day:\s*(.*)', text).group(1).strip()
        appointment_time = re.search(r'appointment_time:\s*(.*)', text).group(1).strip()
    except AttributeError:
        return None, None, None

    return selected_doctor, available_day, appointment_time

def book_appointment_with_chatbot(patient, doctor, day, time):
    try:
        patient_user = User.objects.get(username=patient)
        doctor_user = User.objects.get(username=doctor)
        cleaned_time_str = re.sub(r"[^\d:]", "", time).strip()
        patient_obj = Patient.objects.get(user=patient_user)
        doctor_obj = Doctor.objects.get(user=doctor_user)
        if patient_obj and doctor_obj and day and time:
            if not is_time_between_7am_and_9pm(cleaned_time_str):
                return f"Please Choose time between 7:00 Am to 9:00 Pm"
            else:
                print("time was betwwen 7 to 9")
            if not is_doctor_available(doctor_obj, cleaned_time_str, day):
                return f"Dr. {doctor} is not available at this time. Please choose another  day/time or doctor <br> OR <br> Visit Profile and Check their Busy Schedule: <a href='http://localhost:8000/doctor/doctor_profile/{doctor_user}' target='_blank'> Visit Profile </a>"
            new_appointment = Appointment.objects.create(patient=patient_obj, doctor=doctor_obj, day=day, time=cleaned_time_str)
            email_sent = send_appointment_mail(new_appointment, 'scheduled')
            if email_sent:
                return f"Appointment booked successfully with Dr. {doctor} on {day} at {convert_to_12_hour(new_appointment.time)}. <br><br>Thank you for booking your appointment 🌟 <br><br>Is there anything else I can do for you?"
            else:
                return "Failed to send appointment email."
        else:
            return f"Missing Appointment details"
        pass
    except Exception as e:
        print(e)
        return f"ERROR: {e}"
    

def extract_appointment_id(response):
    pattern = r"appointment_id:\s*(\d+)"
    match = re.search(pattern, response)
    
    if match:
        return int(match.group(1))
    else:
        return None



def is_time_between_7am_and_9pm(time_input):
    def parse_time(time_str):
        parts = time_str.split(':')
        if len(parts) > 2:
            time_str = ':'.join(parts[:2])
        return datetime.datetime.strptime(time_str, '%H:%M').time()

    try:
        if isinstance(time_input, datetime.time):
            time_obj = time_input
        else:
            time_obj = parse_time(time_input)
        
        print("checked time object: ", time_obj)
        if datetime.time(7, 0) <= time_obj <= datetime.time(21, 0):
            return True
        else:
            return False
    except ValueError as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False


def is_doctor_available(doctor, new_time, new_day):
    def parse_time(time_str):
        parts = time_str.split(':')
        if len(parts) > 2:
            time_str = ':'.join(parts[:2])
        else:
            time_str = time_str
        return datetime.datetime.strptime(time_str, '%H:%M').time()
    new_time_obj = parse_time(new_time)
    
    new_time_min = (datetime.datetime.combine(datetime.date.today(), new_time_obj) - datetime.timedelta(minutes=30)).time()
    new_time_max = (datetime.datetime.combine(datetime.date.today(), new_time_obj) + datetime.timedelta(minutes=30)).time()

    existing_appointments = Appointment.objects.filter(doctor=doctor, day=new_day, status="scheduled")

    for appointment in existing_appointments:
        if new_time_min <= appointment.time <= new_time_max:
            return False
    return True

from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

def convert_to_12_hour(time_str):
    time_str = str(time_str)
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    return time_obj.strftime('%I:%M %p').lower()

@csrf_exempt
def send_authentication_mail(email, token, username):
    try:
        subject = 'Verification Mail'
        message = f'Hello {username},\n\nPlease click on the link to authenticate your account.\n\nhttp://{settings.DOMAIN_NAME}/auth/verify/{token}'
        print(message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        data = send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(e)
        return False
    
@csrf_exempt
def send_reset_password_mail(email, token, username):
    try:
        subject = 'Reset Password Mail'
        message = f'Hello {username},\n\nPlease click on the link to reset your password.\n\nhttp://{settings.DOMAIN_NAME}/auth/reset-password/{token}'
        print(message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        data = send_mail(subject, message, email_from, recipient_list)
        return True
    except Exception as e:
        print(e)
        return False

def send_appointment_mail(appointment, action):
    try:
        subject = 'Appointment Update'
        try:
            time = convert_to_12_hour(appointment.time)
        except:
            time = appointment.time
        details = f"\n Here's Appointment Details:\nPatient - {appointment.patient.user.username} \nDoctor - {appointment.doctor.user.username} \nDay - {appointment.day} \nTime - {time} \n"
        if action == 'scheduled':
            message = f'Hello \n\nA new appointment has been scheduled for you on  {appointment.day} at {time}'
        elif action == 'cancelled':
            message = f'Hello \n\nOne of your appointment has been Cancelled.\n'
        elif action == 'completed':
            message = f'Hello, \n\nThank you for compliting your appointment\n'
        else:
            return False
        message += details
        print(message)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [appointment.patient.user.email, appointment.doctor.user.email]
        data = send_mail(subject, message, email_from, recipient_list)
        if data:
            return True
        else:
            return False
    except Exception as e:
        print('MAIL ERROR',e)
        return False


def send_delete_account_mail(user):
    try:
        subject = 'Account Deletion Confirmation'
        message = f'Hello {user.username},\n\nYour account has been deleted successfully.\n'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        data = send_mail(subject, message, email_from, recipient_list)
        if data:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
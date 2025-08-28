from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import User
from doctor.models import *
from patient.models import *
from medic_pro.email_views import send_authentication_mail, send_reset_password_mail, send_delete_account_mail
import uuid
from uuid import uuid4
from django.conf import settings
from django.contrib.auth.hashers import check_password
# Create your views here.


@csrf_exempt
def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, "You're already logged in")
        return redirect('home')
    if request.method == 'POST':
        category = request.POST.get('category')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('password2')
        if category.strip() == "none":
            messages.error(request, "Please Choose Category")
            return redirect('register')
        if password == confirm_password:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.error(request, 'Username or email already exists!')
                return render(request, "auth/register.html")
            else:
                if email == settings.ADMIN_MAIL and category != "admin":
                    messages.error(request, "Admin email can only be used with the admin category.")
                    return render(request, "auth/register.html")
                if category == "admin" and email != settings.ADMIN_MAIL:
                    messages.error(request, "Admin account can only be created with the admin email.")
                    return render(request, "auth/register.html")

                # Create a new user
                newUser = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                if newUser:
                    if category == "admin":
                        newUser.is_superuser = True
                        newUser.is_staff = True
                        newUser.role = "admin"
                    elif category == "doctor":
                        Doctor.objects.create(user=newUser)
                        newUser.role = "doctor"
                    elif category == "patient":
                        Patient.objects.create(user=newUser)
                        newUser.role = "patient"
                    
                newUser.is_active = False
                newUser.save()
                data = send_authentication_mail(newUser.email, newUser.token, newUser.username)
                if data:
                    messages.info(request, "An Email has Sent to your gmail inbox with verification url. Please verify your email")
                    return render(request, "auth/email_sent.html")
                else:
                    print("failled to send email")
                    newUser.delete()
                    messages.error(request, "Something went wrong please try again later.")
                    return redirect('register')
        else:
            messages.error(request, 'Passwords do not match!')
    return render(request, "auth/register.html")


@csrf_exempt
def handleLogin(request):
    if request.user.is_authenticated:
        messages.warning(request, "You're already logged in")
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, 'You have been successfully logged in.')
                return redirect('home')
            else:
                messages.error(
                    request, 'Invalid username or password. Please try again.')
        except Exception as e:
            messages.error(request, "Something went wrong!")

    return render(request, "auth/login.html")


@login_required
def LogoutUser(request):
    logout(request)
    messages.warning(request, "You're Logged out successfully.")
    return redirect('home')


def notLoggedIn(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please Login first")
        return redirect("home")


@csrf_exempt
def resetPassword(request, token):
    try:
        user = User.objects.get(token=token)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            if new_password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, "auth/reset_password.html", {"token":token})
            else:
                user.set_password(new_password)
                if not user.is_active:
                    user.is_active = True
                    messages.success(request, "Account activated successfully")
                user.token = uuid.uuid4()
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect('login')
        
        return render(request, "auth/reset_password.html",{"token":token})
    except Exception as e:
        print(e)
        messages.error(request, "Invalid Token")
        return redirect("home")


@csrf_exempt
def sendResetPasswordEmail(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            email_sent = send_reset_password_mail(user.email, user.token, user.username)
            if email_sent:
                messages.success(request, "Email sent successfully. Check your inbox")
            else:
                messages.error(request, "Email not sent. Please try again")
        except Exception as e:
            print(e)
            messages.error(request, "User not found with this email.")
            return redirect("send_reset_password_mail")
    return render(request, "auth/forgot_password.html")


def emailSent(request):
    messages.info(request, "An Email has Sent to your gmail Account please check you inbox")
    return render(request, "auth/email_sent.html")



@csrf_exempt
def verifyEmail(request, token):
    try:
        user = User.objects.get(token=token)
        if request.method == 'POST':
            password = request.POST.get('password')
            if check_password(password, user.password):
                user.is_active = True
                user.token = uuid4()
                user.save()
                messages.success(request, "Your email has been verified successfully.")
                return redirect('login')
            else:
                messages.error(request, "Incorrect password. Please try again.")
                return render(request, "auth/verify_email_with_password.html", {"token": token})
        return render(request, "auth/verify_email_with_password.html", {"token": token})
    
    except User.DoesNotExist:
        messages.error(request, "Invalid token.")
        return redirect("home")
    except Exception as e:
        print(e)
        messages.error(request, "An error occurred during verification.")
        return redirect("home")



@csrf_exempt
@login_required
def deleteAccount(request):
    if request.method == 'POST':
        user = request.user
        password = request.POST.get('password')
        if user.check_password(password):
            email_sent = send_delete_account_mail(user)
            if email_sent:
                user.delete()
                messages.success(request, "Your account has been deleted successfully")
                return redirect('home')
            else:
                messages.error(request, "Failled to delete your Account. Please check your internet connection")

        else:
            messages.error(request, "Incorrect password")
    
    return render(request, "auth/delete_account.html")



@csrf_exempt
@login_required
def changePassword(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if user.check_password(old_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Your password has been updated successfully")
                return redirect("login")
            else:
                messages.error(request, "New password and confirm password does not match")
        else:
            messages.error(request, "Incorrect old password")
    return render(request, "auth/change_password.html")
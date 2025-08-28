
from django.urls import path
from .views import *
urlpatterns = [
    path("register", registerUser, name="register"),
    path("login", handleLogin, name="login"),
    path("logout", LogoutUser, name="logout"),
    path("email-sent", emailSent , name="email_sent"),
    path('not-logged-in', notLoggedIn, name="not-logged-in"),
    path("verify/<str:token>", verifyEmail, name="verify_token"),
    path("send-reset-password-mail", sendResetPasswordEmail, name="send_reset_password_mail"),
    path("reset-password/<str:token>", resetPassword, name="reset_password"),
    path("delete-account", deleteAccount, name="delete_account"),
    path("change-password", changePassword , name="change_password")
]

from django.urls import path
from .views import *
urlpatterns = [
    path("", index, name="home"),
    path("about", about, name="about"),
    path("contact", contact, name="contact"),
    path("admin_dashboard", admin_dashboard, name="admin_dashboard"),
    path("update_admin_profile", update_admin_profile, name="update_admin_profile"),
    path("chat-bot", chat_bot, name="chat_bot"),
    path("add_new_spec", add_new_spec, name="add_new_spec"),
    path("delete_spec/<int:id>", delete_spec, name="delete_spec")
]
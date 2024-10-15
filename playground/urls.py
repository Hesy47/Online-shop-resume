from django.urls import path
from playground import views

urlpatterns = [
    path("hi/", views.say_hello),
    path("hello/", views.say_hello_html),
    path("email-user/", views.sender_users),
    path("email-admin/", views.sender_admins),
    path("email-attach/", views.sender_attache),
    path("email-jinja/", views.sender_jinja)
]

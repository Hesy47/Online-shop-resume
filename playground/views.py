from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import BadHeaderError, send_mail, mail_admins, EmailMessage
from templated_mail.mail import BaseEmailMessage


def say_hello(request):
    """Just return a simple string respond"""
    return HttpResponse("Hello there!")


def say_hello_html(request):
    """Return the given html page to clint"""
    page_name = "Hello"
    return render(request, "hello.html", {"page_name": page_name})


def sender_users(request):
    try:
        send_mail(
            "welcome",
            "welcome to our website",
            "info@gmail.com",
            ["death19knight@gmail.com"],
        )
    except BadHeaderError:
        pass
    return HttpResponse("email has been send successfully!")


def sender_admins(request):
    try:
        mail_admins(
            "welcome",
            "welcome to our website Admin",
            html_message="This is html form, Admin!",
        )
    except BadHeaderError:
        pass
    return HttpResponse("email has been send successfully!")


def sender_attache(request):
    try:
        message = EmailMessage(
            "photo",
            "check this email for a attached file!",
            "Image@gmail.com",
            ["user1@gmail.com", "user2@gmail.com"],
        )

        message.attach_file("playground/Triss.jpg")
        message.send()

    except BadHeaderError:
        pass

    return HttpResponse("email has been send successfully by attachment!")


def sender_jinja(request):
    try:
        message = BaseEmailMessage(
            template_name="emails/welcome.html",
            context={"name": "Amir"},
        )

        message.send(["me@gmail.com"])

    except BadHeaderError:
        pass

    return HttpResponse("email has been send successfully in Jinja form!")

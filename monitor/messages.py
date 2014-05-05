#encoding=utf-8
from django.core.mail import send_mass_mail


def build_message(recipient_list=['szh1216@gmail.com'], 
        message='alarm', subject="inform", from_email="alarm@moni.com"):
    
    return (subject, message, from_email, recipient_list)
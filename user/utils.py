from dtuotg.settings import EMAIL_HOST_USER
from django.core.mail import send_mail	
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Util:
    @staticmethod
    def send_email(data):
        subject = data['email_subject']
        body = None
        if data['email_body']['check']:
            body = "Hi, " + data['email_body']['username'] + ". " + data['email_body']['message'] + " by using this code : " + str(data['email_body']['code']) + '.'
        else:
            body = "Hi, " + data['email_body']['username'] + ". " + data['email_body']['message'] + " by using this code : " + str(data['email_body']['code']) + " which will expire in 30 minutes"
        send_mail(subject,body,EMAIL_HOST_USER,[data['to_email']])

    def send_invite(data):
        subject = data['email_subject']
        body = "Hi, An invite has been to you to activate your account on DTU-OTG by " + data['email_body']['username'] + "( " + data['email_body']['email'] + " ). " + data['email_body']['message'] + " by using this code : " + (data['email_body']['code']) + "."
        send_mail(subject,body,EMAIL_HOST_USER,[data['to_email']])
    
    def send_report(data):
        subject = data['email_subject']
        body = "Hi," + data['email_body']['message']+ "."
        send_mail(subject,body,EMAIL_HOST_USER,[data['to_email']])
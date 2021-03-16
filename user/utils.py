from dtuotg.settings import EMAIL_HOST_USER
from django.core.mail import send_mail	
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class Util:
    @staticmethod
    def send_email(data):
        print(data['email_subject'])
        subject = data['email_subject']
        body = "Hi, " + data['email_body']['username'] + ". " + data['email_body']['message'] + " by using this link : " + data['email_body']['link']
        send_mail(subject,body,EMAIL_HOST_USER,[data['to_email']])
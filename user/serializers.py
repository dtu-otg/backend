from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from .models import User,Profile
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed,ValidationError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes,smart_str,force_str,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_decode
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
import requests,json
from .exception import *
import re
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)

    class Meta:
        model = User
        fields = ['email','username','password']
         
    def validate(self,attrs):
        email = attrs.get('email','')
        username = attrs.get('username','')

        if not username.isalnum():
            raise ValidationException("The username should only contain alphanumeric characters")
        return attrs
    
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length = 555)
    class Meta:
        model = User
        fields = ['token']

class SendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,required=True)

    class Meta:
        fields = ['email']

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255,read_only=True)
    password = serializers.CharField(max_length = 68,min_length = 6,write_only=True)
    username = serializers.CharField(max_length = 100)
    tokens = serializers.SerializerMethodField()
    first_time_login = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    def get_tokens(self, obj):
        user = User.objects.get(username=obj['username'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }
    def get_first_time_login(self,obj):
        qs = Profile.objects.get(owner__username = obj['username'])
        if qs.name is None:
            return True
        return False

    def get_user_id(self,obj):
        return User.objects.get(username=obj['username']).id

    class Meta:
        model = User
        fields = ['id','username','email','password','tokens','first_time_login','user_id']

    def validate(self,attrs):
        username =  attrs.get('username','')
        password =  attrs.get('password','')
        user_obj_email = User.objects.filter(email=username).first()
        user_obj_username = User.objects.filter(username=username).first()
        if user_obj_email:
            user = auth.authenticate(username = user_obj_email.username,password=password)
            if user_obj_email.auth_provider != 'email':
                raise AuthenticationException(
                    'Please continue your login using ' + filtered_user_by_email[0].auth_provider)
            if not user:
                raise AuthenticationException('Invalid credentials. Try again')
            if not user.is_active:
                raise AuthenticationException('Account disabled. contact admin')
            if not user.is_verified:
                email = user.email
                token = RefreshToken.for_user(user).access_token
                current_site = self.context.get('current_site')
                relative_link = reverse('email-verify')
                absurl = 'https://' + current_site + relative_link + "?token=" + str(token)
                email_body = {}
                email_body['username'] = user.username
                email_body['message'] = 'Use link below to verify your email'
                email_body['link'] = absurl
                data = {'email_body' : email_body,'email_subject' : 'Verify your email','to_email' : user.email}
                Util.send_email(data)
                raise AuthenticationException('Email is not verified, A Verification Email has been sent to your email address')
            return {
                'email' : user.email,
                'username' : user.username,
                'tokens': user.tokens
            }
            return super().validate(attrs)
        if user_obj_username:
            user = auth.authenticate(username = username,password=password)
            if not user:
                raise AuthenticationException('Invalid credentials. Try again')
            if not user.is_active:
                raise AuthenticationException('Account disabled. contact admin')
            if not user.is_verified:
                email = user.email
                token = RefreshToken.for_user(user).access_token
                current_site = self.context.get('current_site')
                relative_link = reverse('email-verify')
                absurl = 'https://' + current_site + relative_link + "?token=" + str(token)
                email_body = {}
                email_body['username'] = user.username
                email_body['message'] = 'Use link below to verify your email'
                email_body['link'] = absurl
                data = {'email_body' : email_body,'email_subject' : 'Verify your email','to_email' : user.email}
                Util.send_email(data)
                raise AuthenticationException('Email is not verified, A Verification Email has been sent to your email address')
            return {
                'email' : user.email,
                'username' : user.username,
                'tokens': user.tokens
            }
            return super().validate(attrs)
        raise AuthenticationException('Invalid credentials. Try again')

class RequestPasswordResetEmailSeriliazer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


    
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationException('The reset link is invalid')

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e:
            raise AuthenticationException('The reset link is invalid')
        return super().validate(attrs)


branches = [
    'bt','ce','co','ee','ec','en','ep','it','me','ae','mc','pe','pt','se','bd'
]

class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    roll_no = serializers.CharField()
    branch = serializers.CharField()
    year = serializers.IntegerField()
    batch = serializers.CharField(allow_blank = True)
    dtu_mail_sent = serializers.SerializerMethodField()

    def get_dtu_mail_sent(self,obj):
        curr_user = self.context.get('user')
        user = User.objects.get(username=curr_user)
        name_here = obj.name.lower()
        roll_no_here = obj.roll_no[:4] + obj.roll_no[5:7] + obj.roll_no[8:]
        email_here = name_here.replace(" ","") + '_' + roll_no_here + '@dtu.ac.in'
        if email_here == user.email or user.dtu_email:
            if user.dtu_email:
                return False
            user.dtu_email = True
            user.save()
            return False
        current_site = self.context.get('current_site',None)
        relative_link = reverse('email-verify')
        #redirect_url = request.GET.get('redirect_url',None)
        token = RefreshToken.for_user(user).access_token
        absurl = 'https://' + current_site + relative_link + "?token=" + str(token) + '&official=True'
        email_body = {}
        email_body['username'] = user.username
        email_body['message'] = 'Verify your official dtu email-id'
        email_body['link'] = absurl
        data = {'email_body' : email_body,'email_subject' : 'DtuOtg - Dtu-Email Verification','to_email' : email_here}
        Util.send_email(data)
        return "A Verification mail has been sent to the offical DTU-Email ID"

    def validate_roll_no(self,obj):
        curr_user = self.context.get('user')
        user = User.objects.get(username=curr_user)
        if len(obj) != 11:
            raise ValidationException('Roll Number is not in proper format, length ' + str(len(obj)) + ' expected : 11')
        if str(obj[:2]) != '2k' and str(obj[:2]) != '2K':
            raise ValidationException('Roll Number is not in proper format, 2K....')
        if str(obj[5:7]).lower() not in branches:
            raise ValidationException('Roll Number is not in proper format, branch not found')
        if int(obj[8:]) == 0:
            raise ValidationException('Roll Number is not in proper format')
        return obj

    def validate_year(self,obj):
        if obj >= 2000 and obj < 2050:
            return obj
        raise ValidationException('Year is not valid')

    def validate_batch(self,obj):
        if obj == None or obj == "":
            return obj
        if len(obj) != 2:
            raise ValidationException('Batch is not correct')
        if obj[:1].lower() < 'a' or obj[:1].lower() > 'b':
            raise ValidationException('Batch is not correct')
        if int(obj[1:]) == 0 or int(obj[1:]) > 16:
            raise ValidationException('Batch is not correct')
        return obj
    
    def validate_branch(self,obj):
        if obj.lower() not in branches:
            raise ValidationException('Invalid Branch')
        return obj.upper()

    class Meta:
        model = Profile
        fields = ['name','roll_no','branch','year','batch','dtu_mail_sent']

class PasswordChangeSerializer(serializers.Serializer):
    old_pass = serializers.CharField(max_length = 68,min_length = 6,required=True)
    new_pass = serializers.CharField(max_length = 68,min_length = 6,required=True)

    class Meta:
        fields = ['old_pass','new_pass']

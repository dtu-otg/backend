from rest_framework import serializers
from rest_framework.serializers import SerializerMethodField
from .models import User,Profile,InviteOnly
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
import random
from datetime import datetime,timedelta
from projects.models import *

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)
    code = serializers.CharField(required = True,write_only=True)

    class Meta:
        model = User
        fields = ['email','username','password','code']
         
    def validate(self,attrs):
        email = attrs.get('email','')
        username = attrs.get('username','')
        code = attrs.get('code',None)
        if not InviteOnly.objects.filter(email=email).exists():
            raise ValidationException("The given email has not been sent an invite")
        orig = InviteOnly.objects.get(email=email).otp
        if code != orig:
            raise ValidationException("The Code is Invalid")
        if not username.isalnum():
            raise ValidationException("The username should only contain alphanumeric characters")
        if email[len(email)-10:].lower() != "@dtu.ac.in":
            raise ValidationException("This email does not belong to DTU ")
        return attrs
    
    def create(self,validated_data):
        del validated_data['code']
        user = User.objects.create_user(**validated_data)
        user.is_verified = True
        user.save()
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    code = serializers.CharField(required= True)

    class Meta:
        model = User
        fields = ['username','code']

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
                verify_code = str(random.randint(0,999999))
                req = 0
                if len(verify_code) < 6:
                    req += 6 - len(verify_code)
                for i in range(req):
                    verify_code = '0' + verify_code
                ele = datetime.now()
                user.code = verify_code
                user.time_code = ele + timedelta(minutes=30)
                user.save()
                email_body = {}
                email_body['username'] = user.username
                email_body['message'] = 'Verify your email'
                email_body['code'] =  verify_code
                email_body['check'] = False
                data = {'email_body' : email_body,'email_subject' : 'DtuOtg - Email Confirmation','to_email' : user.email}
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
                verify_code = str(random.randint(0,999999))
                req = 0
                if len(verify_code) < 6:
                    req += 6 - len(verify_code)
                for i in range(req):
                    verify_code = '0' + verify_code
                ele = datetime.now()
                user.code = verify_code
                user.time_code = ele + timedelta(minutes=30)
                user.save()
                email_body = {}
                email_body['username'] = user.username
                email_body['message'] = 'Verify your email'
                email_body['code'] =  verify_code
                email_body['check'] = False
                data = {'email_body' : email_body,'email_subject' : 'DtuOtg - Email Confirmation','to_email' : user.email}
                Util.send_email(data)
                raise AuthenticationException('Email is not verified, A Verification Email has been sent to your email address')
            return {
                'email' : user.email,
                'username' : user.username,
                'tokens': user.tokens
            }
            return super().validate(attrs)
        raise AuthenticationException('Invalid credentials. Try again')

class RequestPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


    

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    email = serializers.EmailField(
        min_length = 2, write_only=True)
    code = serializers.CharField(max_length = 6)

    class Meta:
        fields = ['email', 'code', 'password']

class PasswordTokenCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(
        min_length = 2, write_only=True)
    code = serializers.CharField(max_length = 6)

    class Meta:
        fields = ['email', 'code',]

branches = [
    'bt','ce','co','ee','ec','en','ep','it','me','ae','mc','pe','pt','se','bd'
]
class ProfileViewSerializer(serializers.ModelSerializer):
    who_sent = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    
    def get_projects(self,obj):
        ans = []    
        user = self.context.get('user',None)
        if user is None:
            return ans
        for ele in Project.objects.filter(owner = User.objects.get(username = user)):
            here = {}
            here['id'] = ele.id
            here['name'] = ele.name
            here['description'] = ele.description
            ans.append(here)
        return ans
    
    
    def get_who_sent(self,obj):
        user = obj.owner
        mail = user.email
        if not InviteOnly.objects.filter(email=mail).exists():
            return " "
        check = InviteOnly.objects.get(email=mail)
        if not User.objects.filter(email=check.sender).exists():
            return " "
        find = User.objects.get(email=check.sender).username
        return find

    class Meta:
        model = Profile
        fields = ['name','roll_no','branch','year','batch','image','who_sent','description','projects']
class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    roll_no = serializers.CharField(required=True)
    branch = serializers.CharField(required=True)
    year = serializers.IntegerField(required=True)
    batch = serializers.CharField(required = True)
    # dtu_mail_sent = serializers.SerializerMethodField()

    # def get_dtu_mail_sent(self,obj):
    #     curr_user = self.context.get('user')
    #     user = User.objects.get(username=curr_user)
    #     name_here = obj.name.lower()
    #     roll_no_here = obj.roll_no[:4] + obj.roll_no[5:7] + obj.roll_no[8:]
    #     email_here = name_here.replace(" ","") + '_' + roll_no_here + '@dtu.ac.in'
    #     if email_here == user.email or user.dtu_email:
    #         if user.dtu_email:
    #             return False
    #         user.dtu_email = True
    #         user.save()
    #         return False
    #     current_site = self.context.get('current_site',None)
    #     relative_link = reverse('email-verify')
    #     #redirect_url = request.GET.get('redirect_url',None)
    #     token = RefreshToken.for_user(user).access_token
    #     absurl = 'https://' + current_site + relative_link + "?token=" + str(token) + '&official=True'
    #     email_body = {}
    #     email_body['username'] = user.username
    #     email_body['message'] = 'Verify your official dtu email-id'
    #     email_body['link'] = absurl
    #     data = {'email_body' : email_body,'email_subject' : 'DtuOtg - Dtu-Email Verification','to_email' : email_here}
    #     Util.send_email(data)
    #     return "A Verification mail has been sent to the offical DTU-Email ID"

    def validate_roll_no(self,obj):
        curr_user = self.context.get('user')
        if len(obj) != 3:
            raise ValidationException('Roll number is not in proper format')
        if int(obj) == 0:
            raise ValidationException('Roll number is not in format format')
        return obj
        #user = User.objects.get(username=curr_user)
        # if len(obj) == 11:
        #     if str(obj[:2]) != '2k' and str(obj[:2]) != '2K':
        #         raise ValidationException('Roll Number is not in proper format, 2K....')
        #     if str(obj[5:7]).lower() not in branches:
        #         if str(obj[5:6]).lower() != 'a' and str(obj[5:6]).lower() != 'b': 
        #             raise ValidationException('Roll Number is not in proper format, batch not found')
        #         if int(obj[6:7]) == 0:
        #             raise ValidationException('Roll Number is not in proper format, batch not found')
        #     if int(obj[8:]) == 0:
        #         raise ValidationException('Roll Number is not in proper format')
        #     return obj
        # if len(obj) == 12:
        #     if str(obj[:2]) != '2k' and str(obj[:2]) != '2K':
        #         raise ValidationException('Roll Number is not in proper format, 2K....')
        #     if str(obj[5:6]).lower()!='a' and str(obj[5:6]).lower()!='b':
        #         raise ValidationException('Roll Number is not in proper format, batch not found')
        #     if int(obj[6:8]) < 1 or int(obj[6:8]) >= 16:
        #         raise ValidationException('Roll Number is not in proper format, batch not found')
        #     if int(obj[9:]) == 0:
        #         raise ValidationException('Roll Number is not in proper format')
        #     return obj
        # raise ValidationException('Roll Number is not in proper format')

    def validate_year(self,obj):
        if obj >= 2000 and obj < 2050:
            return obj
        raise ValidationException('Year is not valid')

    # def validate_batch(self,obj):
    #     # if len(obj) != 2:
    #     #     raise ValidationException('Batch is not correct')
    #     if obj[:1].lower() < 'a' or obj[:1].lower() > 'b':
    #         raise ValidationException('Batch is not correct')
    #     if int(obj[1:]) == 0 or int(obj[1:]) > 16:
    #         raise ValidationException('Batch is not correct')
    #     return obj
    
    def validate_branch(self,obj):
        if obj.lower() not in branches:
            raise ValidationException('Invalid Branch')
        return obj.upper()

    class Meta:
        model = Profile
        fields = ['name','roll_no','branch','year','batch','image','description']

class PasswordChangeSerializer(serializers.Serializer):
    old_pass = serializers.CharField(max_length = 68,min_length = 6,required=True)
    new_pass = serializers.CharField(max_length = 68,min_length = 6,required=True)

    class Meta:
        fields = ['old_pass','new_pass']

class SendInvitesSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length = 2)

    class Meta:
        fields = ['email']
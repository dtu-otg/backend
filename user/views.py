from django.shortcuts import render
from rest_framework import generics,status,permissions,views
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    RequestPasswordResetEmailSerializer,
    SetNewPasswordSerializer,
    SendEmailVerificationSerializer,
    PasswordChangeSerializer,
    PasswordTokenCheckSerializer,
    SendInvitesSerializer,
    ProfileViewSerializer
    )
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,Profile,InviteOnly
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings  
import jwt , json, pytz
from .permissions import *
from rest_framework.generics import RetrieveAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.generics import UpdateAPIView,ListAPIView,ListCreateAPIView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.shortcuts import redirect
from django.http import HttpResponsePermanentRedirect
from django.contrib.auth import authenticate
import os,random
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from datetime import datetime,timedelta
from django.utils import timezone
from rest_framework.parsers import MultiPartParser,FormParser

class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self,request):
        """
        Endpoint for registering a user 
        """
        user = request.data
        serializer = self.serializer_class(data = user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        # user = User.objects.get(email=user_data['email'])
        # verify_code = str(random.randint(0,999999))
        # req = 0
        # if len(verify_code) < 6:
        #     req += 6 - len(verify_code)
        # for i in range(req):
        #     verify_code = '0' + verify_code
        # ele = datetime.now()
        # user.code = verify_code
        # user.time_code = ele + timedelta(minutes=30)
        # user.save()
        # email_body = {}
        # email_body['username'] = user.username
        # email_body['message'] = 'Verify your email'
        # email_body['code'] =  verify_code
        # email_body['check'] = False
        # data = {'email_body' : email_body,'email_subject' : 'DtuOtg - Email Confirmation','to_email' : user.email}
        # Util.send_email(data)
        return Response({'status' : "OK",'result': user_data},status = status.HTTP_201_CREATED)

# algorithm = "HS256"
# class VerifyEmail(views.APIView):
#     serializer_class = EmailVerificationSerializer
    
#     token_param_config = openapi.Parameter(
#         'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
#     @swagger_auto_schema(manual_parameters=[token_param_config])
#     def get(self,request):
#         """
#         Endpoint for verification of the mail
#         """
#         token = request.GET.get('token')
#         official = request.GET.get('official',None)
#         print(official)
#         redirect_url = request.GET.get('redirect_url',None)
#         if redirect_url is None:
#             redirect_url = os.getenv('EMAIL_REDIRECT')
#         try:
#             payload = jwt.decode(token,settings.SECRET_KEY,algorithms = [algorithm])
#             user = User.objects.get(id=payload['user_id'])
#             if not user.dtu_email and official == 'True':
#                 user.dtu_email = True
#                 user.save()
#             if not user.is_verified:
#                 user.is_verified = True
#                 user.save()
#             return redirect(redirect_url + '?email=SuccessfullyActivated')
#         except jwt.ExpiredSignatureError as identifier:
#             return redirect(redirect_url + '?email=ActivationLinkExpired')
#         except jwt.exceptions.DecodeError as identifier:
#             return redirect(redirect_url + '?email=InvalidToken')

class VerifyEmailCode(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    def post(self,request):
        """
        Endpoint for verification of the mail
        """
        data = request.data
        code = data.get('code',None)
        username = data.get('username',None)
        if code is None:
            return Response({'status' : 'Failed',"result" : "Code has not been provided"},status=status.HTTP_400_BAD_REQUEST) 
        if username is None:
            return Response({'status' : 'Failed',"result" : "Username has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(username=username).exists():
            return Response({'status' : 'Failed',"result" : "Username is not valid"},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(username=username)
        if user.is_verified == True:
            return Response({'status' : 'OK',"result" : "You are already verified"},status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        utc = pytz.utc
        start_time = now.replace(tzinfo=utc)
        # print(start_time)
        # print(user.time_code)
        if user.code == code:
            if start_time >= user.time_code.replace(tzinfo=utc):
                return Response({'status' : 'Failed',"result" : "Code has expired"},status=status.HTTP_400_BAD_REQUEST)   
            user.is_verified = True
            user.save()
            return Response({'status' : 'OK',"result" : "You have been verified"},status=status.HTTP_200_OK) 
        else:
            return Response({'status' : 'Failed',"result" : "Incorrect code"},status=status.HTTP_400_BAD_REQUEST)

class LoginApiView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self,request):
        """
        Endpoint for logging in a user
        """
        serializer = self.serializer_class(data=request.data,context = {'current_site' : get_current_site(request).domain})
        serializer.is_valid(raise_exception = True)
        return Response(serializer.data,status = status.HTTP_200_OK)

class CheckAuthView(views.APIView):
    permission_classes = [Authenticated]

    def get(self,request,*args, **kwargs):
        """
        Endpoint for checking if user is authenticated or not by checking if the JWT token is valid or not.
        """
        return Response({'status' : 'OK',"result" : "Token is Valid"},status=status.HTTP_200_OK)


class SendVerificationMail(generics.GenericAPIView):
    serializer_class = SendEmailVerificationSerializer

    def post(self,request,*args, **kwargs):
        """
        Endpoint for sending a verification mail
        """
        email = request.data.get('email',None)
        if email is None:
            return Response({'status' : 'FAILED','error' : 'Email not provided'},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email = email).exists():
            return Response({'status' : 'FAILED','error' :'The given email does not exist'},status = status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
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
        email_body['code'] = verify_code
        email_body['check'] = False
        data = {'email_body' : email_body,'email_subject' : 'DtuOtg - Email Verification','to_email' : user.email}
        Util.send_email(data)
        return Response({'status' : 'OK','result' :'A Verification Email has been sent'},status = status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = RequestPasswordResetEmailSerializer

    def post(self, request):
        """
        Endpoint for sending the password reset email
        """
        serializer = self.serializer_class(data=request.data)

        email = request.data.get('email', '')

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
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
            email_body['message'] = 'Reset your Password'
            email_body['code'] = verify_code
            email_body['check'] = True
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Dtuotg - Password Reset'}
            Util.send_email(data)
            return Response({'status': 'OK','result' :'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Failed','result' :'The given email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = PasswordTokenCheckSerializer

    def post(self,request):
        data = request.data
        email = data.get('email',None)
        code = data.get('code',None)
        if email is None:
            return Response({'status' : 'Failed',"result" : "Email has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if code is None:
            return Response({'status' : 'Failed',"result" : "Code has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email=email).exists():
            return Response({'status' : 'Failed',"result" : "User with the given email does not exist"},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
        if code == user.code:
            return Response({'status': 'OK', 'result': 'Code is Correct'}, status=status.HTTP_200_OK)
        else:
            return Response({'status' : 'Failed',"result" : "Incorrect code"},status=status.HTTP_400_BAD_REQUEST)

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request):
        """
        Endpoint for changing the password in the profile
        """
        data = request.data
        email = data.get('email',None)
        code = data.get('code',None)
        password = data.get('password',None)
        if email is None:
            return Response({'status' : 'Failed',"result" : "Email has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if code is None:
            return Response({'status' : 'Failed',"result" : "Code has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if password is None:
            return Response({'status' : 'Failed',"result" : "Password has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(email=email).exists():
            return Response({'status' : 'Failed',"result" : "User with the given email does not exist"},status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(email=email)
        if code == user.code:
            if len(password) < 6:
                return Response({'status' : 'Failed',"result" : "Password should be of minimum length 6"},status=status.HTTP_400_BAD_REQUEST)
            else:
                user.set_password(password)
                user.save()
                return Response({'status': 'OK', 'result': 'Password reset success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status' : 'Failed',"result" : "Incorrect code"},status=status.HTTP_400_BAD_REQUEST)


class ProfileGetView(generics.RetrieveAPIView):
    serializer_class = ProfileViewSerializer
    permission_classes = [Authenticated]
    queryset = Profile.objects.all()
    lookup_field = "owner_id__username"

    def get_serializer_context(self,**kwargs):
        data = super().get_serializer_context(**kwargs)
        data['user'] = self.request.user.username
        return data
        

class ProfileUpdateView(UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [Authenticated,IsOwner]
    parser_classes = [MultiPartParser,FormParser]
    queryset = Profile.objects.all()
    lookup_field = "owner_id__username"

    def get_serializer_context(self,**kwargs):
        data = super().get_serializer_context(**kwargs)
        data['user'] = self.request.user.username
        data['current_site'] = get_current_site(self.request).domain
        return data

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

class UserProfileUpload(views.APIView):
    permission_classes = [Authenticated]
    parser_classes = [MultiPartParser,FormParser]
    
    def post(self,request,format=None):
        print(request.data)
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePassword(generics.GenericAPIView):
    permission_classes = [Authenticated]
    serializer_class = PasswordChangeSerializer

    def post(self,request,*args,**kwargs):
        """
        Endpoint for changing the password
        """
        data = request.data
        old_pass = data.get('old_pass',None)
        new_pass = data.get('new_pass',None)
        if old_pass is None or new_pass is None:
            return Response({'status' : 'FAILED','error' :'Either the old or new password was not provided'},status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=self.request.user.username,password=old_pass)
        if new_pass == old_pass:
            return Response({'status' : 'FAILED','error' :"The new password is same as the old password"},status=status.HTTP_400_BAD_REQUEST)
        if len(new_pass) < 6:
            return Response({'status' : 'FAILED','error' :"The password is too short, should be of minimum length 6"},status=status.HTTP_400_BAD_REQUEST)
        if user is None:
            return Response({'status' : 'FAILED','error' :"Wrong Password"},status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_pass)
        user.save()
        return Response({'status' : 'OK','result' :"Password Change Complete"},status=status.HTTP_200_OK)

class SendInvitesView(generics.GenericAPIView):
    serializer_class = SendInvitesSerializer
    permission_classes = [AuthenticatedActivated]

    def post(self,request,*args, **kwargs):
        data = request.data
        email = data.get('email',None)
        user = self.request.user
        if user.invites_sent >= 2:
            return Response({'status' : 'FAILED','error' :"You have already exhausted all your invites",'invites_left' : '0'},status=status.HTTP_400_BAD_REQUEST)
        if email[len(email)-10:].lower() != "@dtu.ac.in":
            return Response({'status' : 'FAILED','error' :"This email does not belong to DTU."},status=status.HTTP_400_BAD_REQUEST)
        if InviteOnly.objects.filter(email=email).exists():
            return Response({'status' : 'FAILED','error' :"This email already has an invite sent to it."},status=status.HTTP_400_BAD_REQUEST)
        verify_code = str(random.randint(0,99999999))
        req = 0
        if len(verify_code) < 8:
            req += 8 - len(verify_code)
        for i in range(req):
            verify_code = '0' + verify_code
        ele = datetime.now()
        email_body = {}
        email_body['username'] = user.username
        email_body['email'] = user.email
        email_body['message'] = 'Activate your account by using this code'
        email_body['code'] = verify_code
        email_body['check'] = True
        data = {'email_body': email_body, 'to_email': email,
                'email_subject': 'DTU-OTG Account Activation Mail'}
        Util.send_invite(data)
        InviteOnly.objects.create(email=email,otp=verify_code,sender=user.email)
        user.invites_sent += 1
        user.save()
        return Response({'status': 'OK','result' :'An activation mail has been sent this email',"invites_left" : 2 - user.invites_sent}, status=status.HTTP_200_OK)
        
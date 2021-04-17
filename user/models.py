from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.db.models.signals import post_save
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

def upload_to(instance,filename):
    return 'posts/{filename}'.format(filename=filename)


class UserManager(BaseUserManager):
    def create_user(self,username,email,password=None):
        if username is None:
            raise TypeError('User should have a username')
        if email is None:
            raise TypeError('User should have an email')

        user = self.model(username=username,email = self.normalize_email(email))
        user.set_password(password)
        user.save() 
        return user

    def create_superuser(self,username,email,password=None):
        if password is None:
            raise TypeError('Password should not be none')
        user = self.create_user(username,email,password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save()
        return user




class User(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=100,unique=True,db_index=True)
    email = models.EmailField(max_length=255,unique=True,db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    can_host = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default='email')
    code = models.CharField(max_length = 6,blank = True,null=True)
    time_code = models.DateTimeField(blank=True,null=True)
    USERNAME_FIELD = 'username'
    invites_sent = models.IntegerField(default=0)
    REQUIRED_FIELDS = [ 
        'email'
    ]


    objects = UserManager()

    def __str__(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access': str(refresh.access_token),
        }


class Profile(models.Model):
    owner = models.OneToOneField(User,on_delete = models.CASCADE)
    name = models.CharField(max_length=200,null=True,blank=True)
    roll_no = models.CharField(max_length=50,null=True,blank=True)
    branch = models.CharField(max_length=100,null = True,blank=True)
    year = models.IntegerField(null = True,blank=True)
    batch = models.CharField(max_length=5,null = True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null = True,blank=True)
    updated_at = models.DateTimeField(auto_now = True,null = True,blank=True)
    image = models.ImageField(_("Image"),upload_to=upload_to,default='posts/default.jpeg')

    def __str__(self):
        return str(self.owner) + "'s Profile"

    @receiver(post_save, sender=User)
    def create_Profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(owner=instance)


class InviteOnly(models.Model):
    email = models.EmailField(max_length=255,unique=True,db_index=True)
    otp = models.CharField(max_length = 8,null = True,blank=True)
    sender = models.EmailField(max_length=255,null=True,blank=True)
    def __str__(self):
        return self.email + "'s OTP"
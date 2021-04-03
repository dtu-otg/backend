from django.contrib import admin
from .models import User,Profile,InviteOnly
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(InviteOnly)

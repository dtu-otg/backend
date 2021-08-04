from rest_framework import generics,status,permissions,views,response,mixins
from user.permissions import *
from .models import *
from django.db.models import Q
from .serializers import *
from user.models import User
from rest_framework.parsers import MultiPartParser,FormParser






class CreateProjectView(generics.CreateAPIView):
    permission_classes = [AuthenticatedActivated]
    parser_classes = [MultiPartParser,FormParser]
    serializer_class = CreateProjectSerializer

    def get_serializer_context(self,**kwargs):
        data = super().get_serializer_context(**kwargs)
        data['user'] = self.request.user.username
        return data

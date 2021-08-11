from django.db.models.query import QuerySet
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



class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AuthenticatedActivated, IsOwner]
    parser_classes = [MultiPartParser,FormParser]
    serializer_class = CreateProjectSerializer 
    lookup_field = "id"
    queryset = Project.objects.all()
    
    
class GetProjectView(generics.ListAPIView):
    serializer_class = GetProjectSerializer
    permission_classes = [AuthenticatedActivated]
    queryset = Project.objects.all()

    def get_serializer_context(self,**kwargs):
        data = super().get_serializer_context(**kwargs)
        data['user'] = self.request.user.username
        return data
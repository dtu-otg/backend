from rest_framework import generics,status,permissions,views,response,mixins
from user.permissions import *
from .models import Event
from django.db.models import Q
from .serializers import *

class GetEventsView(generics.ListAPIView):
    serializer_class = GetEventsSerializer
    permission_classes = [AuthenticatedActivated]

    def get_queryset(self):
        uni = self.request.GET.get('university',None)
        society = self.request.GET.get('society',None)
        social = self.request.GET.get('social',None)
        qs = Event.objects.all()
        q = Q()
        if uni != None:
            q |= Q(type_list = '1')
        if society != None:
            q |= Q(type_list = '2')
        if social != None:
            q |= Q(type_list = '3')
        return qs.filter(q).order_by('date_time')
        


    


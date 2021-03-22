from rest_framework import generics,status,permissions,views,response,mixins
from user.permissions import *
from .models import Event,RegistrationEvent
from django.db.models import Q
from .serializers import *
from user.models import User

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
        

class RegisterForEventView(generics.GenericAPIView):
    permission_classes = [AuthenticatedActivated]
    serializer_class = RegistrationEventSerializer

    def post(self,request,*args, **kwargs):
        data = request.data
        username = data.get('username',None)
        event_id = data.get('event_id',None)
        if username is None:
            return response.Response({"status" : 'FAILED','error' :"Username has not been provided"},status=status.HTTP_400_BAD_REQUEST)
        if event_id is None:
            return response.Response({"status" : 'FAILED','error' :"Event_id has not been provided"},status=status.HTTP_400_BAD_REQUEST) 
        user = User.objects.get(username=username)
        event = Event.objects.get(id=event_id)
        if RegistrationEvent.objects.filter(user=user,event=event).exists():
            return response.Response({"status" : 'FAILED','error' :"You are already registered"},status=status.HTTP_400_BAD_REQUEST)
        RegistrationEvent.objects.create(user=user,event=event)
        return response.Response({'status' : 'OK','result' :'Registration for the given event for the given user has been saved'},status=status.HTTP_200_OK)


class CreateEventView(generics.CreateAPIView):
    permission_classes = [Hosting]
    serializer_class = CreateEventSerializer

    def get_serializer_context(self,**kwargs):
        data = super().get_serializer_context(**kwargs)
        data['user'] = self.request.user.username
        return data


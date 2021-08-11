from rest_framework import serializers,status
from .models import Event,RegistrationEvent
from user.models import Profile,User

class GetEventsSerializer(serializers.ModelSerializer):
    type_event = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    registered = serializers.SerializerMethodField()


    def get_registered(self,obj):
        user = self.context.get('user',None)
        if not user:
            return False
        return RegistrationEvent.objects.filter(user__username=user,event=obj).exists()

    def get_owner(self,obj):
        username = obj.owner.username
        return username

    def get_type_event(self,obj):
        if obj.type_event == '1':
            return 'University'
        elif obj.type_event == '2':
            return 'Society'
        else:
            return 'Social'

    class Meta:
        model = Event
        fields = ('id','owner','name','date_time','type_event','registered')

class RegistrationEventSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    event_id = serializers.CharField(required=True)

    class Meta:
        fields = ('username','event_id',)


class CreateEventSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required = True)
    date_time = serializers.DateTimeField(required=True)
    duration = serializers.DurationField(required=True)
    latitude = serializers.DecimalField(required=True,max_digits = 15,decimal_places=9)
    longitude = serializers.DecimalField(required=True,max_digits = 15,decimal_places=9)
    image = serializers.ImageField(required=False)
    user_registered = serializers.SerializerMethodField()

    def get_user_registered(self,obj):
        user = self.context.get('user')
        if user is None:
            return False
        RegistrationEvent.objects.create(event=obj,user=User.objects.get(username=user))
        return True

    class Meta:
        model = Event
        fields = ('owner','name','description','date_time','duration','latitude','longitude','type_event','user_registered','image',)


class EventDetailserializer(serializers.ModelSerializer):
    type_event = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    registered = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    def get_count(self,obj):
        return RegistrationEvent.objects.filter(event=obj).count()
    def get_registered(self,obj):
        user = self.context.get('user',None)
        if user == None:
            return None
        return RegistrationEvent.objects.filter(event = obj,user__username=user).exists()

    def get_owner(self,obj):
        username = obj.owner.username
        return username

    def get_type_event(self,obj):
        if obj.type_event == '1':
            return 'University'
        elif obj.type_event == '2':
            return 'Society'
        else:
            return 'Social'

    class Meta:
        model = Event
        fields = ('id','owner','name','latitude','longitude','description','date_time','duration','type_event','registered','count','image')
        
    
    
class ReportEventsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    
    class Meta:
        fields = ('id',)
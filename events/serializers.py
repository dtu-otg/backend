from rest_framework import serializers,status
from .models import Event
from user.models import Profile

class GetEventsSerializer(serializers.ModelSerializer):
    type_event = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_owner(self,obj):
        name = Profile.objects.get(owner=obj.owner).name
        return name

    def get_type_event(self,obj):
        if obj.type_event == '1':
            return 'University'
        elif obj.type_event == '2':
            return 'Society'
        else:
            return 'Social'

    class Meta:
        model = Event
        fields = ('id','owner','name','latitude','longitude','description','date_time','duration','type_event')

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


    class Meta:
        model = Event
        fields = ('owner','name','description','date_time','duration','latitude','longitude','type_event')
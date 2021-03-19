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
        fields = ('owner','name','latitude','longitude','description','date_time','duration','type_event')
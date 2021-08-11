from rest_framework import serializers,status
from .models import Project
from user.models import Profile,User



class CreateProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    description = serializers.CharField(required = True)
    image = serializers.ImageField(required=False)


    class Meta:
        model = Project
        fields = ('owner','id','name','description','image','discord')
        
class GetProjectSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    def get_owner(self,obj):
        username = obj.owner.username
        return username

    class Meta:
        model = Project
        fields = ('id','owner','name','description','discord','image')
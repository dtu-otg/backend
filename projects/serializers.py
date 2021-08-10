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
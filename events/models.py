from django.db import models
from user.models import User,Profile


TYPE_CHOICES = (
    ("1" , "University"),
    ("2" , "Society"),
    ("3" , "Social"),
)

class Event(models.Model):
    owner = models.ForeignKey(to=User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=True,null=True)
    latitude = models.DecimalField(max_digits = 15,decimal_places=9,null=True,blank=True)
    longitude = models.DecimalField(max_digits = 15,decimal_places=9,null=True,blank=True)
    description = models.TextField(max_length = 300,null = True,blank=True)
    date_time = models.DateTimeField(null = True,blank=True)
    duration = models.DurationField(null = True,blank=True)
    type_event = models.CharField(max_length=1,choices=TYPE_CHOICES,default='1')

    def __str__(self):
        return self.name + " Event"

class RegistrationEvent(models.Model):
    user = models.ForeignKey(to=User,on_delete=models.CASCADE)
    event = models.ForeignKey(to=Event,on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + "'s registration for " + self.event.name
    
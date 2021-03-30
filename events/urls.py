from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',GetEventsView.as_view(),name='get-events'),
    path('details/<int:id>',EventDetailsView.as_view(),name='event-details'),
    path('create/',CreateEventView.as_view(),name='create-events'),
    path('register/',RegisterForEventView.as_view(),name='register-events'),
    path('unregister/',UnRegisterForEventView.as_view(),name='register-events')
]

from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',GetEventsView.as_view(),name='get-events'),
    path('details/<int:id>',EventDetailsView.as_view(),name='event-details'),
    path('create/',CreateEventView.as_view(),name='create-events'),
    path('register/',RegisterForEventView.as_view(),name='register-events'),
    path('unregister/',UnRegisterForEventView.as_view(),name='register-events'),
    path('edit/<int:id>',EventsUpdateView.as_view(),name='edit'),
    path('delete/<int:id>',EventsDeleteView.as_view(),name='delete'),
    path('report/',ReportEvents.as_view(),name = 'report')
]

from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('',GetEventsView.as_view(),name='get-events'),
]

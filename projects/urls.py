from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('create/',CreateProjectView.as_view(),name='create-project'),
]

from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
    path('create/',CreateProjectView.as_view(),name='create-project'),
    path('<int:id>',ProjectDetailView.as_view(),name='project'),
    path('all/',GetProjectView.as_view(),name = 'all-projects')
]

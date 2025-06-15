# facify/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.face_attendance, name='face_attendance'),
]

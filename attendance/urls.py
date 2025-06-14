from django.urls import path
from attendance.views import download_excel
from . import views

urlpatterns = [
    path('download-excel/', download_excel, name='download_excel'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.mark_attendance, name='mark_attendance'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
]
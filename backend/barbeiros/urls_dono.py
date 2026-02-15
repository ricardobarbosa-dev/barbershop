from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_dono, name='dashboard_dono'),
]

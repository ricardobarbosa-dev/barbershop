from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_funcionario, name='dashboard_funcionario'),
]

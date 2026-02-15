from django.urls import path
from .views import listar_notificacoes
from . import views

urlpatterns = [
    path('listar/', listar_notificacoes),
    path('ler/<int:id>/', views.marcar_como_lida),
    path('ler-todas/', views.ler_todas_notificacoes, name='ler_todas_notificacoes'),
]

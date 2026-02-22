from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('cliente/criar/', views.criar_agendamento, name='criar_agendamento'),
    path('cliente/listar/', views.listar_agendamentos, name='listar_agendamentos'),
    path('cliente/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('meus-pacotes/', views.meus_pacotes, name='meus_pacotes'),
    path('barbeiro/<int:user_id>/', views.perfil_barbeiro, name='perfil_barbeiro'),
    path('avaliar/<int:agendamento_id>/', views.avaliar_barbeiro, name='avaliar_barbeiro'),
    path('dashboard/barbeiro/', views.dashboard_barbeiro, name='dashboard_barbeiro'),
    path('agendamento/<int:agendamento_id>/concluir/',views.concluir_agendamento,name='concluir_agendamento'),
    path('agendamento/<int:agendamento_id>/<str:status>/',views.atualizar_status_agendamento,name='atualizar_status_agendamento'),
    path('dashboard/agenda/', views.configurar_agenda, name='agenda'),
    path('agenda/excluir/<int:id>/', views.excluir_disponibilidade, name='excluir_disponibilidade'),
    path('buscar-horarios/', views.buscar_horarios_ajax, name='buscar_horarios_ajax'),
    path('dashboard/minha-agenda/', views.agenda_barbeiro, name='minha_agenda_barbeiro'),
    path('quitar-debito/<int:cliente_id>/', views.quitar_debito, name='quitar_debito'),
    path('dashboard/devedores/', views.lista_devedores, name='lista_devedores'),
    path('bloquear/', views.bloquear_agenda, name='bloquear_agenda'),
    path('remover-bloqueio/<int:pk>/', views.remover_bloqueio, name='remover_bloqueio'),
    path('dashboard/pacotes/', views.gerenciar_pacotes, name='gerenciar_pacotes'),
    path('dashboard/pacotes/adicionar/', views.adicionar_pacote_cliente, name='adicionar_pacote_cliente'),
    path('dashboard/pacote/remover/<int:pk>/', views.remover_pacote, name='remover_pacote'),
]

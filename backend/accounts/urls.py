from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import perfil_cliente

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('login/telefone/', views.telefone_login_view, name='telefone_login'),
    path('login/otp/', views.verificar_otp_view, name='verificar_otp'),
    path('register/', views.register, name='register'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_done.html"), name="password_reset_complete"),
    path('perfil/', perfil_cliente, name='perfil_cliente'),
    path('historico/', views.historico_cliente, name='historico_cliente'),
    # path('editar-perfil/', views.editar_perfil_barbeiro, name='editar_perfil_barbeiro'),
    path('perfil/editar/', views.editar_perfil_barbeiro, name='editar_perfil_barbeiro'),
    path('redirect/', views.redirect_dashboard, name='redirect_dashboard'), 
]



 
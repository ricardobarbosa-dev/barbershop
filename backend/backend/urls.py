from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),

    path('', include('agendamentos.urls')),
    
    path('barbeiros/', include('barbeiros.urls')),  
    path('dashboard/funcionario/', include('barbeiros.urls_funcionario')),
    path('dashboard/dono/', include('barbeiros.urls_dono')),

    path('notificacoes/', include('notificacoes.urls')),

    path(
    'senha/',
    auth_views.PasswordChangeView.as_view(
        template_name='cliente/trocar_senha.html',
        success_url='/accounts/perfil/'
    ),
    name='trocar_senha'
),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

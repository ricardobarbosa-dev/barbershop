from django.contrib import admin
from .models import Notificacao
from django.contrib.auth.models import User

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'mensagem', 'lida', 'criada_em')

@admin.action(description="Enviar notificação para usuários selecionados")
def enviar_notificacao(modeladmin, request, queryset):

    for user in queryset:
        Notificacao.objects.create(
            usuario=user,
            mensagem="📢 Você recebeu uma nova mensagem da barbearia!"
        )

class UserAdmin(admin.ModelAdmin):
    actions = [enviar_notificacao]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

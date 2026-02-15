from django.db.models.signals import post_save
from django.dispatch import receiver
from agendamentos.models import Agendamento
from .models import Notificacao
from datetime import datetime, timedelta


@receiver(post_save, sender=Agendamento)
def criar_notificacao_agendamento(sender, instance, created, **kwargs):

    if created:

        Notificacao.objects.create(
            usuario=instance.cliente,
            mensagem=f"✅ Agendamento confirmado para {instance.data} às {instance.horario}"
        )

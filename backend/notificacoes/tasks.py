from agendamentos.models import Agendamento
from .models import Notificacao
from datetime import datetime, timedelta
from django.utils import timezone


def notificacoes_automaticas():

    agora = timezone.localtime()

    hoje = agora.date()

    agendamentos = Agendamento.objects.filter(
        data=hoje,
        status='PENDENTE'
    )

    for ag in agendamentos:

        horario_ag = datetime.combine(ag.data, ag.horario)
        horario_ag = timezone.make_aware(horario_ag)

        diff = horario_ag - agora

        # meia noite
        if agora.hour == 0 and agora.minute < 5:

            Notificacao.objects.get_or_create(
                usuario=ag.cliente,
                mensagem=f"💈 Você tem um corte HOJE às {ag.horario}"
            )

        # 30 minutos antes
        if timedelta(minutes=29) <= diff <= timedelta(minutes=31):

            Notificacao.objects.get_or_create(
                usuario=ag.cliente,
                mensagem=f"⏰ Seu corte é em 30 minutos!"
            )

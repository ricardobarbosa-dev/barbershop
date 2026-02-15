from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from agendamentos.models import Agendamento
from .decorators import apenas_funcionario
from django.utils import timezone
from django.db.models import Sum

@login_required
@apenas_funcionario
def dashboard_funcionario(request):
    barbeiro = request.user.barbeiro
    agendamentos = Agendamento.objects.filter(
        barbeiro=barbeiro,
        status__in=Agendamento.STATUS_ATIVOS
    ).select_related('cliente', 'servico').order_by('data', 'horario')

    hoje = timezone.localdate()

    cortes_hoje = Agendamento.objects.filter(
        barbeiro=barbeiro,
        status=Agendamento.STATUS_CONCLUIDO,
        data=hoje
    ).count()

    inicio_mes = hoje.replace(day=1)
    cortes_mes = Agendamento.objects.filter(
        barbeiro=barbeiro,
        status=Agendamento.STATUS_CONCLUIDO,
        data__gte=inicio_mes
    ).count()

    faturamento_mes = Agendamento.objects.filter(
        barbeiro=barbeiro,
        status=Agendamento.STATUS_CONCLUIDO,
        data__gte=inicio_mes
    ).aggregate(total=Sum('servico__preco'))['total'] or 0
    context = {
        'agendamentos': agendamentos,
        'cortes_hoje': cortes_hoje,
        'cortes_mes': cortes_mes,
        'faturamento_mes': faturamento_mes,
    }

    return render(request, 'barbeiros/dashboard_funcionario.html', context)


@login_required
def dashboard_dono(request):
    return render(request, 'barbeiros/dashboard_dono.html')
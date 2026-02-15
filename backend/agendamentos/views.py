from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Sum, Case, When, Value, IntegerField
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.urls import reverse
# models
from .models import Agendamento, NivelFidelidade, PacoteCorte, Avaliacao, DisponibilidadeBarbeiro, BloqueioAgenda
from servicos.models import Servico
from barbeiros.models import Barbeiro
from barbearia.models import ConfiguracaoBarbearia
from .utils import gerar_slots_horarios

# ==========================================
# VIEWS DO CLIENTE
# ==========================================

@login_required
def dashboard_cliente(request):
    user = request.user
    cortes_realizados = Agendamento.objects.filter(cliente=user, status='CONCLUIDO').count()

    config = ConfiguracaoBarbearia.objects.first()
    cortes_para_brinde = config.cortes_para_brinde if config else 10
    faltam = max(cortes_para_brinde - cortes_realizados, 0)

    agendamentos = Agendamento.objects.filter(cliente=user).annotate(
        prioridade=Case(
            When(status='PENDENTE', then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
    ).order_by('prioridade', 'data', 'horario')[:5]

    niveis = NivelFidelidade.objects.order_by("cortes_necessarios")
    cargo_cliente = "Cliente"
    proximo_nivel = None

    for nivel in niveis:
        if cortes_realizados >= nivel.cortes_necessarios:
            cargo_cliente = nivel.nome
        elif not proximo_nivel:
            proximo_nivel = nivel

    faltam_para_nivel = None
    if proximo_nivel:
        faltam_para_nivel = proximo_nivel.cortes_necessarios - cortes_realizados

    return render(request, 'agendamentos/dashboard_cliente.html', {
        'user': user,
        'cortes_realizados': cortes_realizados,
        'agendamentos': agendamentos,
        'cortes_para_brinde': cortes_para_brinde,
        'faltam': faltam,
        'cargo_cliente': cargo_cliente,
        'proximo_nivel': proximo_nivel.nome if proximo_nivel else None,
        'faltam_para_nivel': faltam_para_nivel,
    })

@login_required 
def listar_agendamentos(request):
    status = request.GET.get('status', 'PENDENTE')
    agendamentos = Agendamento.objects.filter(
        cliente=request.user,
        status=status
    ).select_related('servico', 'barbeiro').order_by('-data', '-horario')

    total_pendentes = Agendamento.objects.filter(cliente=request.user, status='PENDENTE').count()
    total_concluidos = Agendamento.objects.filter(cliente=request.user, status='CONCLUIDO').count()
    total_cancelados = Agendamento.objects.filter(cliente=request.user, status='CANCELADO').count()

    return render(request, 'agendamentos/listar_agendamentos.html', {
        'agendamentos': agendamentos,
        'status_atual': status,
        'total_pendentes': total_pendentes,
        'total_concluidos': total_concluidos,
        'total_cancelados': total_cancelados,
    })

@login_required
def criar_agendamento(request):
    servicos = Servico.objects.all()
    barbeiros = Barbeiro.objects.filter(ativo=True)

    if request.method == 'POST':
        servico_id = request.POST.get('servico')
        barbeiro_id = request.POST.get('barbeiro')
        data = request.POST.get('data')
        horario = request.POST.get('horario')

        if not all([servico_id, barbeiro_id, data, horario]):
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('criar_agendamento')

        # Verifica ocupação (incluindo bloqueios)
        existe = Agendamento.objects.filter(
            barbeiro_id=barbeiro_id,
            data=data,
            horario=horario
        ).exclude(status='CANCELADO').exists() 

        if existe:
            messages.error(request, 'Este horário já está ocupado. Escolha outro.')
            return redirect('criar_agendamento')

        try:
            Agendamento.objects.create(
                cliente=request.user,
                servico_id=servico_id,
                barbeiro_id=barbeiro_id,
                data=data,
                horario=horario,
                status='PENDENTE' 
            )
            messages.success(request, 'Agendamento criado com sucesso!')
            return redirect('listar_agendamentos')
        except Exception as e:
            messages.error(request, f'Erro ao salvar: {e}')
            return redirect('criar_agendamento')

    return render(request, 'agendamentos/criar_agendamento.html', {
        'servicos': servicos,
        'barbeiros': barbeiros
    })

@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, cliente=request.user)
    if request.method == "POST":
        if agendamento.status == 'PENDENTE':
            agendamento.status = 'CANCELADO'
            agendamento.save()
            messages.success(request, 'Agendamento cancelado!')
        else:
            messages.error(request, 'Este agendamento não pode ser cancelado.')
    return redirect('listar_agendamentos')

# ==========================================
# VIEWS DO BARBEIRO (DASHBOARD E AGENDA)
# ==========================================

@login_required
def dashboard_barbeiro(request):
    barbeiro = get_object_or_404(Barbeiro, user=request.user)
    hoje = timezone.localdate()
    inicio_mes = hoje.replace(day=1)

    agendamentos_hoje = Agendamento.objects.filter(
        barbeiro=barbeiro, data=hoje, status__in=['PENDENTE', 'AGENDADO'], E_BLOQUEIO=False
    ).select_related('cliente', 'servico')

    concluidos_hoje = Agendamento.objects.filter(barbeiro=barbeiro, data=hoje, status='CONCLUIDO')
    concluidos_mes = Agendamento.objects.filter(barbeiro=barbeiro, data__gte=inicio_mes, status='CONCLUIDO')

    faturamento_hoje = concluidos_hoje.aggregate(total=Sum('servico__preco'))['total'] or 0
    faturamento_mes = concluidos_mes.aggregate(total=Sum('servico__preco'))['total'] or 0

    return render(request, 'barbeiro/dashboard.html', {
        'agendamentos_hoje': agendamentos_hoje,
        'total_hoje': agendamentos_hoje.count(),
        'cortes_hoje': concluidos_hoje.count(),
        'faturamento_hoje': faturamento_hoje,
        'cortes_mes': concluidos_mes.count(),
        'faturamento_mes': faturamento_mes,
    })

@login_required
def agenda_barbeiro(request):
    is_prof = request.user.is_staff or request.user.groups.filter(name='funcionario').exists()
    if not is_prof:
        return redirect('dashboard_cliente')

    barbeiro_perfil = get_object_or_404(Barbeiro, user=request.user)
    data_str = request.GET.get('data')
    data_filtro = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else timezone.localdate()

    agendamentos = Agendamento.objects.filter(
        barbeiro=barbeiro_perfil, 
        data=data_filtro
    ).select_related('cliente', 'servico').order_by('horario')

    return render(request, 'barbeiro/minha_agenda.html', {
        'agendamentos': agendamentos,
        'data_selecionada': data_filtro
    })

@login_required
def concluir_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    if agendamento.status != 'CONCLUIDO':
        pacote = PacoteCorte.objects.filter(
            cliente=agendamento.cliente, 
            ativo=True
        ).first()

        if pacote:
            if not pacote.expirado() and pacote.cortes_restantes() > 0:
                pacote.cortes_usados += 1
                
                if pacote.cortes_restantes() <= 0:
                    pacote.ativo = False
                
                pacote.save()
                messages.info(request, f"Corte debitado do pacote! Restam {pacote.cortes_restantes()}.")
            else:
                pacote.ativo = False
                pacote.save()
                messages.warning(request, "O pacote deste cliente expirou ou acabou.")

        agendamento.status = 'CONCLUIDO'
        agendamento.save()
        messages.success(request, "Atendimento concluído com sucesso!")

    return redirect('minha_agenda_barbeiro')

@login_required
def gerenciar_pacotes(request):
    if not request.user.is_staff:
        return redirect('home')

    pacotes = PacoteCorte.objects.all().order_by('-ativo', '-data_inicio')
    clientes = User.objects.filter(is_staff=False).order_by('username')

    return render(request, 'agendamentos/gerenciar_pacotes.html', {
        'pacotes': pacotes,
        'clientes_list': clientes,
        'data_selecionada': timezone.now()
    })

@login_required
def atualizar_status_agendamento(request, agendamento_id, status):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    agendamento.status = status.upper()
    agendamento.save()
    messages.success(request, f"Status alterado!")
    
    url = reverse('minha_agenda_barbeiro')
    return redirect(f"{url}?data={agendamento.data}")

# ==========================================
# BLOQUEIO DE HORÁRIOS
# ==========================================
@login_required
def bloquear_agenda(request):
    if request.method == 'POST':
        barbeiro = get_object_or_404(Barbeiro, user=request.user)
        data = request.POST.get('data')
        inicio = datetime.strptime(request.POST.get('hora_inicio'), '%H:%M')
        fim = datetime.strptime(request.POST.get('hora_fim'), '%H:%M')
        motivo = request.POST.get('motivo', 'Bloqueio')

        disp = DisponibilidadeBarbeiro.objects.filter(barbeiro=request.user).first()
        intervalo = disp.intervalo_minutos if disp else 30

        atual = inicio
        while atual < fim:
            Agendamento.objects.get_or_create(
                barbeiro=barbeiro, data=data, horario=atual.time(),
                defaults={
                    'cliente': request.user, 'servico': Servico.objects.first(),
                    'status': 'CONCLUIDO', 'E_BLOQUEIO': True, 'OBSERVACAO': motivo
                }
            )
            atual += timedelta(minutes=intervalo)

        messages.success(request, 'Agenda bloqueada!')
        
        url = reverse('minha_agenda_barbeiro')
        return redirect(f"{url}?data={data}")

@login_required
def remover_bloqueio(request, pk):
    agendamento = get_object_or_404(Agendamento, pk=pk)
    data = agendamento.data
    agendamento.delete()
    messages.success(request, "Horário liberado!")
    
    url = reverse('minha_agenda_barbeiro')
    return redirect(f"{url}?data={data}")

# ==========================================
# DISPONIBILIDADE E AJAX
# ==========================================

@login_required
def configurar_agenda(request):
    if request.method == 'POST':
        dia = request.POST.get('dia_semana')
        inicio = request.POST.get('hora_inicio')
        fim = request.POST.get('hora_fim')
        intervalo = int(request.POST.get('intervalo', 0))

        DisponibilidadeBarbeiro.objects.update_or_create(
            barbeiro=request.user, dia_semana=dia,
            defaults={'hora_inicio': inicio, 'hora_fim': fim, 'intervalo_minutos': intervalo}
        )
        messages.success(request, "Disponibilidade atualizada!")
        return redirect('agenda')

    configuracoes = DisponibilidadeBarbeiro.objects.filter(barbeiro=request.user).order_by('dia_semana')
    return render(request, 'barbeiro/agenda.html', {'configuracoes': configuracoes})

@login_required
def excluir_disponibilidade(request, id):
    get_object_or_404(DisponibilidadeBarbeiro, id=id, barbeiro=request.user).delete()
    return redirect('agenda')


def buscar_horarios_ajax(request):
    barbeiro_id = request.GET.get('barbeiro')
    data_str = request.GET.get('data')
    
    if not (barbeiro_id and data_str): 
        return JsonResponse({'horarios': []})

    data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
    
    disp = DisponibilidadeBarbeiro.objects.filter(
        barbeiro_id=barbeiro_id, 
        dia_semana=data_obj.weekday(), 
        ativo=True
    ).first()
    
    if not disp: 
        return JsonResponse({'horarios': []})

    ocupados = Agendamento.objects.filter(
        barbeiro_id=barbeiro_id, 
        data=data_obj
    ).exclude(status='CANCELADO').values_list('horario', flat=True)

    bloqueios = BloqueioAgenda.objects.filter(
        barbeiro_id=barbeiro_id,
        data=data_obj
    )
    
    slots = []
    atual = datetime.combine(data_obj, disp.hora_inicio)
    fim = datetime.combine(data_obj, disp.hora_fim)
    agora = datetime.now()

    while atual < fim:
        horario_time = atual.time()
        
        esta_ocupado = horario_time in ocupados
        
        esta_bloqueado = any(b.hora_inicio <= horario_time < b.hora_fim for b in bloqueios)
        
        ja_passou = atual <= agora

        slots.append({
            'hora': horario_time.strftime('%H:%M'),
            'disponivel': not (esta_ocupado or esta_bloqueado or ja_passou)
        })
        
        atual += timedelta(minutes=disp.intervalo_minutos)
    
    return JsonResponse({'horarios': slots})

# ==========================================
# PACOTES E AVALIAÇÕES
# ==========================================

@login_required
def meus_pacotes(request):
    pacotes = PacoteCorte.objects.filter(cliente=request.user).order_by('-data_inicio')
    return render(request, 'agendamentos/meus_pacotes.html', {'pacotes': pacotes})

@login_required
def adicionar_pacote_cliente(request):
    if request.method == 'POST' and request.user.is_staff:
        cliente_id = request.POST.get('cliente')
        cliente = get_object_or_404(User, id=cliente_id)
        
        PacoteCorte.objects.filter(cliente=cliente, ativo=True).update(ativo=False)
        PacoteCorte.objects.create(
            cliente=cliente,
            total_cortes=4,
            cortes_usados=0,
            ativo=True
        )
        
        messages.success(request, f"Pacote de 4 cortes ativado para {cliente.first_name}!")
    return redirect('gerenciar_pacotes')

@login_required
def remover_pacote(request, pk):
    pacote = get_object_or_404(PacoteCorte, pk=pk)
    nome_cliente = pacote.cliente.get_full_name() or pacote.cliente.username
    pacote.delete()
    messages.success(request, f"Pacote de {nome_cliente} removido com sucesso!")
    return redirect('gerenciar_pacotes')

def perfil_barbeiro(request, user_id):
    barbeiro_user = get_object_or_404(User, id=user_id)
    
    avaliacoes = Avaliacao.objects.filter(barbeiro=barbeiro_user)
    media = avaliacoes.aggregate(media=Avg('nota'))['media'] or 0
    
    ja_avaliou = False
    if request.user.is_authenticated:
        ja_avaliou = Avaliacao.objects.filter(
            cliente=request.user, 
            barbeiro=barbeiro_user
        ).exists()

    return render(request, 'agendamentos/perfil_barbeiro.html', {
        'barbeiro': barbeiro_user, 
        'perfil': barbeiro_user.profile, 
        'media': media, 
        'total': avaliacoes.count(),
        'star_range': range(1, 6),
        'ja_avaliou': ja_avaliou 
    })

@login_required
def avaliar_barbeiro(request, agendamento_id):
    if request.method == "POST":
        agendamento = get_object_or_404(Agendamento, id=agendamento_id)
        try:
            barbeiro_target = agendamento.barbeiro.user
        except AttributeError:
            barbeiro_target = agendamento.barbeiro.usuario if hasattr(agendamento.barbeiro, 'usuario') else agendamento.barbeiro

        nota = request.POST.get('nota')

        if Avaliacao.objects.filter(cliente=request.user, barbeiro=barbeiro_target).exists():
            messages.warning(request, f"Você já avaliou o perfil de {barbeiro_target.first_name}!")
        else:
            Avaliacao.objects.create(
                cliente=request.user,
                barbeiro=barbeiro_target,
                agendamento=agendamento,
                nota=nota
            )
            messages.success(request, "Avaliação enviada com sucesso! ⭐")

        return redirect('perfil_barbeiro', user_id=barbeiro_target.id)
    
    return redirect('home')
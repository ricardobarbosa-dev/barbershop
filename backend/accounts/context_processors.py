from agendamentos.models import Agendamento, NivelFidelidade

def fidelidade_cliente(request):

    if not request.user.is_authenticated:
        return {}

    user = request.user

    cortes_realizados = Agendamento.objects.filter(
        cliente=user,
        status='CONCLUIDO'
    ).count()

    niveis = NivelFidelidade.objects.order_by("cortes_necessarios")

    nivel_atual = "Cliente"
    proximo_nivel = None

    for nivel in niveis:
        if cortes_realizados >= nivel.cortes_necessarios:
            nivel_atual = nivel.nome
        elif not proximo_nivel:
            proximo_nivel = nivel

    faltam_para_nivel = None
    if proximo_nivel:
        faltam_para_nivel = proximo_nivel.cortes_necessarios - cortes_realizados

    return {
        'cargo_cliente': nivel_atual,
        'faltam_para_nivel': faltam_para_nivel,
        'proximo_nivel': proximo_nivel.nome if proximo_nivel else None,
    }

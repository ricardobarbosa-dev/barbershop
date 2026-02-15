from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notificacao
from django.views.decorators.http import require_POST

from django.shortcuts import get_object_or_404

@login_required
def listar_notificacoes(request):

    notificacoes = Notificacao.objects.filter(
        usuario=request.user,
        lida=False
    )[:10]

    data = [
        {
            "id": n.id,
            "mensagem": n.mensagem,
            "criada": n.criada_em.strftime("%H:%M")
        }
        for n in notificacoes
    ]

    return JsonResponse(data, safe=False)

@login_required
@require_POST
def marcar_como_lida(request, id):

    try:
        notificacao = Notificacao.objects.get(
            id=id,
            usuario=request.user
        )

        notificacao.lida = True
        notificacao.save()

        return JsonResponse({"status":"ok"})

    except Notificacao.DoesNotExist:
        return JsonResponse({"status":"erro"})


@login_required
@require_POST
def ler_todas_notificacoes(request):
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
    return JsonResponse({'success': True})
def menu_usuario(request):
    if not request.user.is_authenticated:
        return {'menu_items': []}
    if request.user.is_staff or request.user.groups.filter(name='Barbeiro').exists():
        menu = [
            {'label': 'Dashboard', 'icon': 'bi-grid', 'url': '/dashboard/'},
            {'label': 'Agenda', 'icon': 'bi-calendar-check', 'url': '/agenda/'},
            {'label': 'Adicionar Pacote', 'icon': 'bi-plus-circle', 'url': '/pacotes/novo/'},
        ]
    else:
        menu = [
            {'label': 'Início', 'icon': 'bi-house', 'url': '/'},
            {'label': 'Dados', 'icon': 'bi-person', 'url': '/perfil/'},
            {'label': 'Pacotes', 'icon': 'bi-box', 'url': '/meus-pacotes/'},
            {'label': 'Histórico', 'icon': 'bi-clock-history', 'url': '/historico/'},
            {'label': 'Reserva', 'icon': 'bi-calendar-plus', 'url': '/criar/'},
        ]

    return {'menu_items': menu}
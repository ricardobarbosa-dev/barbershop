from django.shortcuts import redirect

class CheckUserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.path == '/':
            
            if hasattr(request.user, 'barbeiro'):
                tipo = request.user.barbeiro.tipo
                
                if tipo == 'DONO':
                    return redirect('dashboard_dono')
                
                elif tipo == 'FUNCIONARIO':
                    return redirect('dashboard_barbeiro')
            
            else:
                return redirect('dashboard_cliente')

        return response
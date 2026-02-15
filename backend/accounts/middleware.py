from django.shortcuts import redirect
from django.urls import reverse

class CheckUserTypeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.path == '/' and 'site' not in request.GET:
            if hasattr(request.user, 'barbeiro'):
                return redirect('dashboard_barbeiro')
            return redirect('dashboard_cliente')
        return response


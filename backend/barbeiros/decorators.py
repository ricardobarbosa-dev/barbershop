from django.shortcuts import redirect

def apenas_funcionario(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'barbeiro'):
            return redirect('home')  
        if request.user.barbeiro.tipo != 'FUNCIONARIO':
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

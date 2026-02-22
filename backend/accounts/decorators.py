from django.shortcuts import redirect
from django.contrib import messages

def no_access(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, 'Deslogue para acessar essa página!')
            return redirect('redirect_dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
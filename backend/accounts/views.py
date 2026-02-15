from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import OTP, Profile
from .services import enviar_sms
import traceback, random
from django import forms
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, ProfileForm, ExtendedUserCreationForm
from agendamentos.models import Agendamento
from django.core.paginator import Paginator
from .decorators import no_access


# Login tradicional
@no_access
def login_view(request):
    if request.user.is_authenticated:
        return redirect('redirect_dashboard')

    if request.method == 'POST':
        login_input = request.POST.get('username') 
        senha = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=login_input)
            username_to_auth = user_obj.username 
        except User.DoesNotExist:
            username_to_auth = login_input
        user = authenticate(request, username=username_to_auth, password=senha)

        if user:
            login(request, user)
            messages.success(request, '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m430-500 283-283q12-12 28-12t28 12q12 12 12 28t-12 28L487-444l-57-56Zm99 99 254-255q12-12 28.5-12t28.5 12q12 12 12 28.5T840-599L586-345l-57-56ZM211-211q-91-91-91-219t91-219l120-120 59 59q7 7 12 14.5t10 15.5l148-149q12-12 28.5-12t28.5 12q12 12 12 28.5T617-772L444-599l-85 84 19 19q46 46 44 110t-49 111l-57-56q23-23 25.5-54.5T321-440l-47-46q-12-12-12-28.5t12-28.5l57-56q12-12 12-28.5T331-656l-64 64q-68 68-68 162.5T267-267q68 68 163 68t163-68l239-240q12-12 28.5-12t28.5 12q12 12 12 28.5T889-450L649-211q-91 91-219 91t-219-91Zm219-219ZM680-39v-81q66 0 113-47t47-113h81q0 100-70.5 170.5T680-39ZM39-680q0-100 70.5-170.5T280-921v81q-66 0-113 47t-47 113H39Z"/></svg> Bem-vindo de volta!')
            return redirect('redirect_dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


# register account
@no_access
def register(request):
    if request.user.is_authenticated:
        messages.warning(request, '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="M508.5-291.5Q520-303 520-320t-11.5-28.5Q497-360 480-360t-28.5 11.5Q440-337 440-320t11.5 28.5Q463-280 480-280t28.5-11.5ZM440-440h80v-240h-80v240Zm40 360q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg> Deslogue para criar um novo cadastro!')
        return redirect('redirect_dashboard') 

    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard_cliente') 
    else:
        form = ExtendedUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
    
# Login via Telefone (OTP)
@no_access
def telefone_login_view(request):
    if request.method == 'POST':
        telefone = request.POST.get('telefone', '').strip()
        telefone = ''.join(filter(str.isdigit, telefone)) 

        if not telefone:
            messages.warning(request, 'Informe um número de telefone válido.')
            return redirect('telefone_login')

        user, _ = User.objects.get_or_create(
            username=telefone,
            defaults={'email': f'{telefone}@otp.com'}
        )

        ultimo = OTP.objects.filter(user=user).last()
        if ultimo and ultimo.criado_em + timedelta(seconds=60) > timezone.now():
            messages.error(request, 'Aguarde 60 segundos para pedir um novo código.')
            return redirect('telefone_login')

        codigo = str(random.randint(100000, 999999))
        OTP.objects.create(
            user=user,
            codigo=codigo,
            expira_em=timezone.now() + timedelta(minutes=5)
        )

        enviar_sms(telefone, f'Seu código Barbershop é: {codigo}')
        request.session['otp_user'] = user.id
        messages.success(request, 'Código enviado com sucesso para seu celular!')
        return redirect('verificar_otp')

    return render(request, 'accounts/telefone_login.html')

# Verificação do código
def verificar_otp_view(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        user_id = request.session.get('otp_user')
        otp = OTP.objects.filter(user_id=user_id, usado=False).last()

        if not otp or not otp.is_valido():
            messages.error(request, 'Código expirado ou inexistente.')
            return redirect('verificar_otp')

        if otp.codigo != codigo:
            otp.tentativas += 1
            if otp.tentativas >= 5:
                otp.bloqueado_ate = timezone.now() + timedelta(minutes=5)
            otp.save()
            messages.error(request, 'Código incorreto. Tente novamente.')
            return redirect('verificar_otp')

        otp.usado = True
        otp.save()
        login(request, otp.user)
        messages.success(request, 'Acesso autorizado! Seja bem-vindo.')
        return redirect('/')

    return render(request, 'accounts/verificar_otp.html')
    
# Perfil Cliente
@login_required
def perfil_cliente(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        try:
            if 'old_password' in request.POST:
                senha_form = PasswordSimpleForm(request.user, request.POST)
                
                if senha_form.is_valid():
                    user = senha_form.save()
                    update_session_auth_hash(request, user)
                    return JsonResponse({
                        'success': True, 
                        'message': '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m424-296 282-282-56-56-226 226-114-114-56 56 170 170Zm56 216q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg> Senha alterada com sucesso!'
                    })
                else:
                    error_msg = "Dados inválidos"
                    if senha_form.errors:
                        error_msg = list(senha_form.errors.values())[0][0]
                    
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    }, status=400) 

            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                return JsonResponse({
                    'success': True,
                    'message': ' <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m424-296 282-282-56-56-226 226-114-114-56 56 170 170Zm56 216q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/></svg> Perfil atualizado com sucesso!'
                })

            return JsonResponse({
                'success': False,
                'message': 'Verifique os campos do perfil.',
                'errors': {'user': u_form.errors, 'profile': p_form.errors}
            }, status=400)

        except Exception as e:
            print(f"ERRO NO SERVIDOR: {str(e)}")
            traceback.print_exc()
            return JsonResponse({
                'success': False, 
                'message': f'Erro interno: {str(e)}'
            }, status=200) 

    u_form = UserUpdateForm(instance=request.user)
    p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'cliente/perfil.html', {
        'u_form': u_form,
        'p_form': p_form,
        'profile': profile
    })

# Troca de Senha
class PasswordSimpleForm(PasswordChangeForm):
    new_password2 = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        if new_password1:
            self.cleaned_data["new_password2"] = new_password1
        return cleaned_data


def trocar_senha(request):
    if request.method == 'POST':
        form = PasswordSimpleForm(request.user, request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            messages.success(request, ' Sua senha foi alterada com sucesso!')
            return redirect('perfil_cliente')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    break 
            
            return redirect('perfil_cliente')
    
    return redirect('perfil_cliente')

# historico
@login_required
def historico_cliente(request):

    agendamentos_lista = Agendamento.objects.filter(
        cliente=request.user
    ).select_related('barbeiro', 'servico').order_by('-data', '-horario')

    paginator = Paginator(agendamentos_lista, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cliente/historico.html', {
        'page_obj': page_obj
    })

# avaliacao
@login_required
def editar_perfil_barbeiro(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado!")
            return redirect('dashboard_barbeiro')

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        'accounts/editar_perfil_barbeiro.html',
        {'form': form}
    )

# redirect 
@login_required
def redirect_dashboard(request):
    user = request.user
    if user.groups.filter(name='dono').exists():
        return redirect('dashboard_dono')
    if user.groups.filter(name='funcionario').exists():
        return redirect('dashboard_funcionario')
    return redirect('dashboard_cliente')

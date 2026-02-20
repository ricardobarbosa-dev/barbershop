from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import OTP, Profile, BarberPhoto
from .services import enviar_sms
import traceback, random
from django import forms
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm, ProfileForm, ExtendedUserCreationForm, BarberPhotoForm
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
            messages.success(request, 'Bem-vindo de volta!')
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
        messages.warning(request, 'Deslogue para criar um novo cadastro!')
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
                        'message': 'Senha alterada com sucesso!'
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
                    'message': 'Perfil atualizado com sucesso!'
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
    status_atual = request.GET.get('status', 'PENDENTE')

    agendamentos_lista = Agendamento.objects.filter(
        cliente=request.user,
        status=status_atual
    ).select_related('barbeiro', 'servico').order_by('-data', '-horario')

    paginator = Paginator(agendamentos_lista, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_pendentes = Agendamento.objects.filter(cliente=request.user, status='PENDENTE').count()
    total_concluidos = Agendamento.objects.filter(cliente=request.user, status='CONCLUIDO').count()
    total_cancelados = Agendamento.objects.filter(cliente=request.user, status='CANCELADO').count()

    return render(request, 'cliente/historico.html', {
        'page_obj': page_obj,            
        'status_atual': status_atual,
        'total_pendentes': total_pendentes,
        'total_concluidos': total_concluidos,
        'total_cancelados': total_cancelados,
    })
# avaliacao
@login_required
def editar_perfil_barbeiro(request):
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        photo_form = BarberPhotoForm(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            
            if photo_form.is_valid() and 'image' in request.FILES:
                nova_foto = photo_form.save(commit=False)
                nova_foto.profile = profile  
                nova_foto.save()
                messages.success(request, "Foto adicionada à galeria!")
            
            messages.success(request, "Perfil atualizado!")
            return redirect('perfil_barbeiro', user_id=request.user.id)
    else:
        form = ProfileForm(instance=profile)
        photo_form = BarberPhotoForm()

    return render(
        request,
        'accounts/editar_perfil_barbeiro.html',
        {
            'form': form,
            'photo_form': photo_form,  
            'perfil': profile
        }
    )

# delete gallery
@login_required
def excluir_foto_galeria(request, foto_id):
    foto = get_object_or_404(BarberPhoto, id=foto_id, profile=request.user.profile)
    if request.method == 'POST':
        foto.delete()
        messages.success(request, "Foto removida com sucesso!")
    
    return redirect('editar_perfil_barbeiro')

# redirect 
@login_required
def redirect_dashboard(request):
    user = request.user
    try:
        perfil = user.profile
        tipo_usuario = perfil.tipo
    except Profile.DoesNotExist:
        tipo_usuario = Profile.CLIENTE

    if tipo_usuario in [Profile.DONO, Profile.FUNCIONARIO]:
        return redirect('dashboard_barbeiro')
    
    return redirect('dashboard_cliente')
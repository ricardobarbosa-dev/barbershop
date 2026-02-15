from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
import re

class UserUpdateForm(forms.ModelForm):
    # Definimos como required=False para o Django não travar a validação
    # e disabled=True para o Django ignorar qualquer tentativa de alteração no POST
    email = forms.EmailField(
        label="Email",
        required=False, 
        disabled=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'readonly': 'readonly', # Reforço no HTML
            'style': 'color: #888; cursor: not-allowed;'
        })
    )

    first_name = forms.CharField(
        label="Nome",
        min_length=4,
        max_length=30,
        error_messages={
            'min_length': 'O nome deve ter pelo menos 4 caracteres.',
            'max_length': 'O nome pode ter no máximo 30 caracteres.',
            'required': 'O campo nome é obrigatório.'
        },
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    last_name = forms.CharField(
        label="Sobrenome",
        min_length=4,
        max_length=30,
        error_messages={
            'min_length': 'O sobrenome deve ter pelo menos 4 caracteres.',
            'max_length': 'O sobrenome pode ter no máximo 30 caracteres.',
            'required': 'O campo sobrenome é obrigatório.'
        },
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_first_name(self):
        nome = self.cleaned_data.get('first_name')
        if nome and any(char.isdigit() for char in nome):
            raise forms.ValidationError('O nome não pode conter números.')
        return nome.title() if nome else nome

    def clean_last_name(self):
        sobrenome = self.cleaned_data.get('last_name')
        if sobrenome and any(char.isdigit() for char in sobrenome):
            raise forms.ValidationError('O sobrenome não pode conter números.')
        return sobrenome.title() if sobrenome else sobrenome

class ProfileUpdateForm(forms.ModelForm):

    telefone = forms.CharField(
        required=False,
        min_length=10,
        max_length=15,
        error_messages={
            'min_length': 'Telefone inválido.',
            'max_length': 'Telefone muito longo.'
        },
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Profile
        fields = ['foto', 'telefone']

    def clean_telefone(self):

        telefone = self.cleaned_data.get('telefone')

        if not telefone:
            return telefone

        telefone = re.sub(r'\D', '', telefone)

        if len(telefone) < 10:
            raise forms.ValidationError('Telefone inválido.')

        return telefone

class ProfileForm(forms.ModelForm): 
    class Meta:
        model = Profile
        fields = ['foto', 'banner', 'localizacao', 'whatsapp', 'instagram', 'facebook', 'site_pessoal']        
        labels = {
            'localizacao': 'Sua Localização',
            'whatsapp': 'WhatsApp (apenas números)',
            'site_pessoal': 'Seu Site ou Link'
        }
        widgets = {
            'foto': forms.FileInput(attrs={'class': 'input-file-hidden'}),
            'banner': forms.FileInput(attrs={'class': 'input-file-hidden'}),
        }

class ExtendedUserCreationForm(UserCreationForm):
    first_name = forms.CharField(label='Nome', max_length=30, required=True)
    last_name = forms.CharField(label='Sobrenome', max_length=30, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name')
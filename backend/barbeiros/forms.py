from django import forms
from .models import PerfilBarbeiro

class PerfilBarbeiroForm(forms.ModelForm):
    class Meta:
        model = PerfilBarbeiro
        fields = ['localizacao', 'whatsapp', 'instagram', 'facebook', 'site_pessoal']
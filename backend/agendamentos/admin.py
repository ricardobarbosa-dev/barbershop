from django.contrib import admin
from .models import Agendamento, NivelFidelidade, PacoteCorte   

admin.site.register(Agendamento)

# Fidelidade
@admin.register(NivelFidelidade)
class NivelFidelidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "cortes_necessarios")
    ordering = ("cortes_necessarios",)

# Pacote
@admin.register(PacoteCorte)
class PacoteCorteAdmin(admin.ModelAdmin):
    list_display = (
        'cliente',
        'total_cortes',
        'cortes_usados',
        'data_inicio',
        'data_fim',
        'ativo'
    )
    list_filter = ('ativo',)
    search_fields = ('cliente__username', 'cliente__email')
from django.contrib import admin
from .models import ConfiguracaoBarbearia


@admin.register(ConfiguracaoBarbearia)
class ConfigAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return not ConfiguracaoBarbearia.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

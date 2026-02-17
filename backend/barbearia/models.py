from django.db import models

class ConfiguracaoBarbearia(models.Model):
    cortes_para_brinde = models.PositiveIntegerField(
        default=10,
        verbose_name="Cortes necessários para ganhar brinde"
    )
    mensagem_brinde = models.CharField(
        max_length=255,
        default="Parabéns! Você ganhou um brinde 🎉"
    )
    def __str__(self):
        return "Configurações da Barbearia"
    class Meta:
        verbose_name = "Configuração"
        verbose_name_plural = "Brinde"


class BloqueioData(models.Model):
    data = models.DateField(unique=True)
    motivo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Bloqueio: {self.data}"
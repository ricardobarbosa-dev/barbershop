from django.db import models
from django.contrib.auth.models import User

class Barbeiro(models.Model):
    TIPO_CHOICES = (
        ('FUNCIONARIO', 'Funcionário'),
        ('DONO', 'Dono'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='barbeiro'
    )
    nome = models.CharField(max_length=100)
    comissao = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ativo = models.BooleanField(default=True)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='FUNCIONARIO')

    def __str__(self):
        return self.nome

from django.db import models

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    duracao_minutos = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.nome} - R$ {self.preco}'

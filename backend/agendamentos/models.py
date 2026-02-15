from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from barbeiros.models import Barbeiro
from servicos.models import Servico
from django.utils import timezone
from datetime import timedelta

class Agendamento(models.Model):
    STATUS_PENDENTE = 'PENDENTE'
    STATUS_AGENDADO = 'AGENDADO'
    STATUS_CANCELADO = 'CANCELADO'
    STATUS_CONCLUIDO = 'CONCLUIDO'

    STATUS_CHOICES = (
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_AGENDADO, 'Agendado'),
        (STATUS_CANCELADO, 'Cancelado'),
        (STATUS_CONCLUIDO, 'Concluído'),
    )

    STATUS_ATIVOS = [
        STATUS_PENDENTE,
        STATUS_AGENDADO,
    ]

    STATUS_HISTORICO = [
        STATUS_CANCELADO,
        STATUS_CONCLUIDO,
    ]

    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='agendamentos'
    )

    barbeiro = models.ForeignKey(
        Barbeiro,
        on_delete=models.CASCADE,
        related_name='agendamentos'
    )

    E_BLOQUEIO = models.BooleanField(default=False) 
    OBSERVACAO = models.CharField(max_length=100, blank=True, null=True) 

    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    status = models.CharField(
        max_length=15,  
        choices=STATUS_CHOICES,
        default=STATUS_PENDENTE
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('barbeiro', 'data', 'horario')
        ordering = ['-data', '-horario'] 

    def __str__(self):
        return f'{self.cliente.username} - {self.servico.nome} - {self.data} {self.horario}'


class NivelFidelidade(models.Model):
    nome = models.CharField(max_length=50)
    cortes_necessarios = models.PositiveIntegerField()
    cor = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["cortes_necessarios"]

    def __str__(self):
        return f"{self.nome} ({self.cortes_necessarios} cortes)"


class PacoteCorte(models.Model):
    cliente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pacotes'
    )
    total_cortes = models.PositiveIntegerField(default=4)
    cortes_usados = models.PositiveIntegerField(default=0)
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(blank=True)
    ativo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.data_fim:
            self.data_fim = self.data_inicio + timedelta(days=30)
        super().save(*args, **kwargs)

    def cortes_restantes(self):
        return self.total_cortes - self.cortes_usados

    def expirado(self):
        return timezone.now() > self.data_fim

    def __str__(self):
        return f"{self.cliente.username} - {self.cortes_restantes()} cortes restantes"


class Avaliacao(models.Model):
    barbeiro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    agendamento = models.ForeignKey('Agendamento', on_delete=models.CASCADE, null=True, blank=True)    
    nota = models.IntegerField()
    comentario = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('barbeiro', 'cliente')


class DisponibilidadeBarbeiro(models.Model):
    barbeiro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.IntegerField(choices=[
        (0, 'Segunda-feira'),
        (1, 'Terça-feira'),
        (2, 'Quarta-feira'),
        (3, 'Quinta-feira'),
        (4, 'Sexta-feira'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    ])
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    intervalo_minutos = models.IntegerField(default=30) 
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.barbeiro.username} - {self.get_dia_semana_display()}"


class BloqueioAgenda(models.Model):
    MOTIVOS_CHOICES = [
        ('ALMOCO', 'Horário de Almoço'),
        ('PARTICULAR', 'Assunto Particular'),
        ('FOLGA', 'Folga'),
        ('OUTRO', 'Outro'),
    ]

    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name='bloqueios')
    data = models.DateField()
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()
    motivo = models.CharField(max_length=20, choices=MOTIVOS_CHOICES, default='ALMOCO')

    class Meta:
        verbose_name = 'Bloqueio de Agenda'
        verbose_name_plural = 'Bloqueios de Agenda'

    def __str__(self):
        return f"Bloqueio {self.barbeiro} - {self.data} ({self.hora_inicio}-{self.hora_fim})"
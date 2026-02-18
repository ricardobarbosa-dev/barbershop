from django.db import models
from django.contrib.auth.models import User 

class Notificacao(models.Model):
    TIPOS = (
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
        ('INFO', 'Informação'),
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='INFO') # Novo campo
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f'Notificação para {self.usuario.username} - {"Lida" if self.lida else "Não lida"}'

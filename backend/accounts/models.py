from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField()

    tentativas = models.PositiveIntegerField(default=0)
    usado = models.BooleanField(default=False)
    bloqueado_ate = models.DateTimeField(null=True, blank=True) 

    def is_valido(self):
        if self.usado:
            return False
        if self.bloqueado_ate and timezone.now() < self.bloqueado_ate:
            return False
        return timezone.now() <= self.expira_em
    
class Profile(models.Model):
    CLIENTE = 'cliente'
    FUNCIONARIO = 'funcionario'
    DONO = 'dono'

    TIPOS = [
        (CLIENTE, 'Cliente'),
        (FUNCIONARIO, 'Funcionário'),
        (DONO, 'Dono'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default=CLIENTE
    )

    telefone = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='profiles/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)

    localizacao = models.CharField(max_length=255, blank=True, null=True)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    site_pessoal = models.URLField(max_length=200, blank=True, null=True)
    anos_experiencia = models.PositiveIntegerField(default=0, blank=True, null=True)
    cortes_feitos = models.PositiveIntegerField(default=0, blank=True, null=True)
    especialidade = models.CharField(max_length=100, blank=True, null=True, default="Barbeiro Profissional")

    def __str__(self):
        return f"{self.user.username} ({self.get_tipo_display()})"
    
@receiver(post_save, sender=User)
def criar_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)


class BarberPhoto(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='barber_gallery/')
    description = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.profile.user.username}"
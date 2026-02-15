from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import OTP

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        OTP.objects.filter(expira_em__lt=timezone.now()).delete()

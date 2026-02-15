from twilio.rest import Client
from django.conf import settings

def enviar_sms(telefone, mensagem):
    client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)

    client.messages.create(
        body=mensagem,
        from_=settings.TWILIO_PHONE,  
        to=telefone                   
    )

from datetime import datetime, timedelta

def gerar_slots_horarios(hora_inicio, hora_fim, intervalo_minutos):
    slots = []
    atual = datetime.combine(datetime.today(), hora_inicio)
    fim = datetime.combine(datetime.today(), hora_fim)
    
    while atual < fim:
        slots.append(atual.time())
        atual += timedelta(minutes=intervalo_minutos)
        
    return slots
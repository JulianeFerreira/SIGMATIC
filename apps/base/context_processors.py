from django.conf import settings
from .views import obter_modulos_dinamicos

def menu_superior_global(request):
    try:
        modulos, _ = obter_modulos_dinamicos()
    except Exception:
        modulos = []
        
    return {
        'modulos': modulos
    }
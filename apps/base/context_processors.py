from django.conf import settings
from .views import obter_modulos_dinamicos  # Importa a função que você já tem pronta

def menu_superior_global(request):
    """
    Injeta automaticamente a variável 'modulos' em todos os templates do projeto,
    garantindo que o base_sesp.html sempre renderize o menu superior.
    """
    try:
        modulos, _ = obter_modulos_dinamicos()
    except Exception:
        modulos = []
        
    return {
        'modulos': modulos
    }
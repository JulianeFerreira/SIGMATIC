# apps/base/views.py
import requests
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from apps.base.core.models import ModuloSistema 

def menu_principal(request):
    return render(request, 'base_sesp/home_sesp.html')

@csrf_exempt
def gateway_base_roteador(request, nome_modulo, caminho_restante):
 
    try:
        modulo = ModuloSistema.objects.get(slug=nome_modulo)
        if not modulo.ativo:
            return JsonResponse({"erro": f"O módulo '{modulo.nome}' está em manutenção."}, status=503)

        url_destino = f"{modulo.url_destino.rstrip('/')}/{caminho_restante}"
        
        try:
            resposta = requests.request(
                method=request.method,
                url=url_destino,
                params=request.GET,
                data=request.body if request.body else None,
                headers={'Content-Type': request.headers.get('Content-Type', 'application/json')},
                timeout=10
            )
            return HttpResponse(
                content=resposta.content, 
                status=resposta.status_code, 
                content_type=resposta.headers.get('Content-Type', 'application/json')
            )
        except requests.exceptions.RequestException:
            return JsonResponse({"erro": f"O servidor do módulo '{modulo.nome}' está offline."}, status=502)

    except ModuloSistema.DoesNotExist:
        return JsonResponse({"erro": f"Módulo '{nome_modulo}' não encontrado no banco dinâmico."}, status=404)
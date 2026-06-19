from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse


def menu_principal(request):
    pasta_apps = settings.BASE_DIR / "apps"
    
    pastas_ignoradas = ["base", "core", "usuarios", "organizacao", "acessos", "migrations"]
    
    modulos_para_front = []

    if pasta_apps.exists():
        for pasta_mod in pasta_apps.iterdir():
            if pasta_mod.is_dir() and not pasta_mod.name.startswith("__") and pasta_mod.name not in pastas_ignoradas:
                
                nome_modulo_pasta = pasta_mod.name
                nome_modulo_formatado = nome_modulo_pasta.replace("_", " ").title()
                
                submodulos_encontrados = []
                
                for pasta_sub in pasta_mod.iterdir():
                    if pasta_sub.is_dir() and not pasta_sub.name.startswith("__") and pasta_sub.name not in pastas_ignoradas:
                        submodulos_encontrados.append({
                            "nome": pasta_sub.name.replace("_", " ").title(),
                            "url": f"/{nome_modulo_pasta}/{pasta_sub.name}/" 
                        })
                
                submodulos_encontrados = sorted(submodulos_encontrados, key=lambda x: x['nome'])

                modulos_para_front.append({
                    "nome": nome_modulo_formatado,
                    "url_raiz": f"/{nome_modulo_pasta}/",
                    "submodulos": submodulos_encontrados
                })

    modulos_para_front = sorted(modulos_para_front, key=lambda x: x['nome'])


    return render(request, "base_sesp/home_sesp.html", {"modulos": modulos_para_front, "query_original": None})

def pesquisa(request):
    query = request.GET.get('q', '').strip().lower()
    
    pasta_apps = settings.BASE_DIR / "apps"
    pastas_ignoradas = ["base", "core", "usuarios", "organizacao", "acessos", "migrations"]
    
    modulos_para_front = []
    resultados_busca = [] 

    if pasta_apps.exists():
        for pasta_mod in pasta_apps.iterdir():
            if pasta_mod.is_dir() and not pasta_mod.name.startswith("__") and pasta_mod.name not in pastas_ignoradas:
                nome_modulo_pasta = pasta_mod.name
                nome_modulo_formatado = nome_modulo_pasta.replace("_", " ").title()
                
                submodulos_encontrados = []
                
                if query and query in nome_modulo_formatado.lower():
                    resultados_busca.append({
                        "tipo": "Módulo Principal",
                        "nome": nome_modulo_formatado,
                        "url": f"/{nome_modulo_pasta}/"
                    })

                for pasta_sub in pasta_mod.iterdir():
                    if pasta_sub.is_dir() and not pasta_sub.name.startswith("__") and pasta_sub.name not in pastas_ignoradas:
                        nome_sub_formatado = pasta_sub.name.replace("_", " ").title()
                        url_sub = f"/{nome_modulo_pasta}/{pasta_sub.name}/"
                        
                        submodulos_encontrados.append({
                            "nome": nome_sub_formatado,
                            "url": url_sub
                        })
                        
                        if query and query in nome_sub_formatado.lower():
                            resultados_busca.append({
                                "tipo": f"Submódulo de {nome_modulo_formatado}",
                                "nome": nome_sub_formatado,
                                "url": url_sub
                            })

                submodulos_encontrados = sorted(submodulos_encontrados, key=lambda x: x['nome'])
                modulos_para_front.append({
                    "nome": nome_modulo_formatado,
                    "url_raiz": f"/{nome_modulo_pasta}/",
                    "submodulos": submodulos_encontrados
                })

    modulos_para_front = sorted(modulos_para_front, key=lambda x: x['nome'])

    if request.GET.get('ajax') == '1':
        return JsonResponse({"resultados": resultados_busca})

    contexto = {
        "modulos": modulos_para_front,
        "query_original": request.GET.get('q', ''),
        "resultados": resultados_busca
    }
    return render(request, "base_sesp/home_sesp.html", contexto)
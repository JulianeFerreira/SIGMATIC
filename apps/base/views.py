from django.shortcuts import render
from django.conf import settings

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


    return render(request, "base_sesp/home_sesp.html", {"modulos": modulos_para_front})
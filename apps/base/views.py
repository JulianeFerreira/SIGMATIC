from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.http import Http404

def obter_modulos_dinamicos(query=None):
    pasta_apps = settings.BASE_DIR / "apps"
    pasta_templates = settings.BASE_DIR / "templates"
    pastas_ignoradas = ["base", "organizacao", "acessos", "migrations"]
    
    modulos_para_front = []
    resultados_busca = []

    if not pasta_apps.exists():
        return modulos_para_front, resultados_busca
        
    if query:
        query = query.lower()

    for pasta_mod in pasta_apps.iterdir():
        if pasta_mod.is_dir() and not pasta_mod.name.startswith("__") and pasta_mod.name not in pastas_ignoradas:
            nome_modulo_pasta = pasta_mod.name
            nome_modulo_formatado = nome_modulo_pasta.replace("_", " ").upper()
            
            submodulos_encontrados = []
            
            if query and query in nome_modulo_formatado.lower():
                resultados_busca.append({
                    "tipo": "Módulo Principal",
                    "nome": nome_modulo_formatado,
                    "url": f"/{nome_modulo_pasta}/"
                })

            for arquivo_app in pasta_mod.rglob("apps.py"):
                pasta_sub = arquivo_app.parent 
                
                if pasta_sub.name not in pastas_ignoradas and not pasta_sub.name.startswith("__"):
                    nome_sub_pasta = pasta_sub.name
                    nome_sub_formatado = nome_sub_pasta.replace("_", " ").upper()
                    
                    partes_caminho = pasta_sub.relative_to(pasta_apps).parts
                    url_sub = "/" + "/".join(partes_caminho) + "/"
                    
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
                        
                    # =========================================================
                    # 3. BUSCA PROFUNDA: PROCURA ABAS/TELAS
                    # =========================================================
                    if query:
                        caminho_tpl_sub = pasta_templates.joinpath(*partes_caminho)
                        
                        if caminho_tpl_sub.exists():
                            for arquivo_html in caminho_tpl_sub.glob("*.html"):
                                nome_arquivo = arquivo_html.stem
                                
                                if nome_arquivo in ['dashboard', 'index', 'base']:
                                    continue
                                
                                nome_tela = nome_arquivo.replace("_", " ").title()
                                
                                if query in nome_tela.lower():
                                    resultados_busca.append({
                                        "tipo": f"Aba/Tela em {nome_sub_formatado}",
                                        "nome": nome_tela,
                                        "url": f"{url_sub}{nome_arquivo}/"
                                    })

            submodulos_encontrados = sorted(submodulos_encontrados, key=lambda x: x['nome'])
            
            modulos_para_front.append({
                "nome": nome_modulo_formatado,
                "url_raiz": f"/{nome_modulo_pasta}/",
                "submodulos": submodulos_encontrados
            })

    modulos_para_front = sorted(modulos_para_front, key=lambda x: x['nome'])
    return modulos_para_front, resultados_busca

# ==========================================
# AS VIEWS REAIS QUE RESPONDEM AO NAVEGADOR
# ==========================================

def menu_principal(request):

    modulos, _ = obter_modulos_dinamicos()
    return render(request, "base_sesp/home_sesp.html", {"modulos": modulos, "query_original": None})


def pesquisa(request):
    query = request.GET.get('q', '').strip().lower()
    
    modulos, resultados = obter_modulos_dinamicos(query)
    
    if request.GET.get('ajax') == '1':
        return JsonResponse({"resultados": resultados})

    contexto = {
        "modulos": modulos,
        "query_original": request.GET.get('q', ''),
        "resultados": resultados
    }
    return render(request, "base_sesp/home_sesp.html", contexto)

def carregar_template_dinamico(request, caminho):
    caminho_limpo = caminho.strip('/')
    ultima_parte = caminho_limpo.split('/')[-1]
    
    arquivos_para_tentar = [
        f"{caminho_limpo}.html",
        f"{caminho_limpo}/dashboard.html",
        f"{caminho_limpo}/{ultima_parte}.html",
    ]
    
    modulos, _ = obter_modulos_dinamicos()
    
    partes_caminho = caminho_limpo.split('/')
    if len(partes_caminho) >= 2:
        base_url = f"/{partes_caminho[0]}/{partes_caminho[1]}"
    else:
        base_url = f"/{caminho_limpo}"

    contexto = {
        "modulos": modulos,
        "base_url": base_url,
        "url_atual": request.path
    }
    
    for template_path in arquivos_para_tentar:
        try:
            get_template(template_path)
            return render(request, template_path, contexto)
        except TemplateDoesNotExist:
            continue
            
    raise Http404(f"O sistema procurou, mas não encontrou nenhum arquivo HTML para o caminho: {caminho_limpo}")

def carrega_submodulo_dinamico_profundo(request, modulo, nivel2, submodulo):
    caminho_tpl = f"{modulo}/{nivel2}/{submodulo}/dashboard.html"
    modulos, _ = obter_modulos_dinamicos()
    try:
        get_template(caminho_tpl)
        return render(request, caminho_tpl, {"modulos": modulos})
    except TemplateDoesNotExist:
        return render(request, "base_sesp/home_sesp.html", {
            "modulos": modulos, 
            "modulo_em_criacao": f"{modulo} / {nivel2} / {submodulo}"
        })
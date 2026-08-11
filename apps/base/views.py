from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.conf import settings
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

# ==============================================================================
# 1. HELPER DE INFRAESTRUTURA
# ==============================================================================

def _encontrar_template_dinamico(caminho_relativo):

    caminho_limpo = caminho_relativo.strip('/')
    partes = caminho_limpo.split('/')
    ultima_parte = partes[-1].lower() if partes else ""

    template_direto = f"{caminho_limpo}.html"
    try:
        get_template(template_direto)
        return template_direto
    except TemplateDoesNotExist:
        pass

    pasta_templates = settings.BASE_DIR / "templates"
    diretorio_alvo = pasta_templates.joinpath(*partes)

    if diretorio_alvo.is_dir():
        arquivos_html = list(diretorio_alvo.glob("*.html"))
        if arquivos_html:
            mapa_html = {f.stem.lower(): f for f in arquivos_html}
            prioridades = ['index', 'dashboard', ultima_parte]
            
            for nome_prioritario in prioridades:
                if nome_prioritario in mapa_html:
                    arquivo = mapa_html[nome_prioritario]
                    return str(arquivo.relative_to(pasta_templates))

            return str(arquivos_html[0].relative_to(pasta_templates))

    return None


# ==============================================================================
# 2. MOTOR DE BUSCA E DESCOBERTA DE MÓDULOS
# ==============================================================================

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
                        
                    if query:
                        caminho_tpl_sub = pasta_templates.joinpath(*partes_caminho)
                        
                        if caminho_tpl_sub.exists():
                            for arquivo_html in caminho_tpl_sub.glob("*.html"):
                                nome_arquivo = arquivo_html.stem
                                
                                if nome_arquivo.lower() in ['base', 'layout', '_partial']:
                                    continue
                                
                                nome_tela = nome_arquivo.replace("_", " ").title()
                                
                                if query in nome_tela.lower():
                                    resultados_busca.append({
                                        "tipo": f"Submodulo/De {nome_sub_formatado}",
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


# ==============================================================================
# 3. CONTROLADORAS DE EXIBIÇÃO E ROTEAMENTO
# ==============================================================================

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
    partes_caminho = caminho_limpo.split('/')
    
    modulos, _ = obter_modulos_dinamicos()
    base_url = f"/{partes_caminho[0]}/{partes_caminho[1]}" if len(partes_caminho) >= 2 else f"/{caminho_limpo}"

    contexto = {
        "modulos": modulos,
        "base_url": base_url,
        "url_atual": request.path
    }
    
    template_escolhido = _encontrar_template_dinamico(caminho_limpo)
    
    if template_escolhido:
        return render(request, template_escolhido, contexto)

    raise Http404(f"Arquivo ou diretório HTML não encontrado: {caminho_limpo}")


def carrega_submodulo_dinamico_profundo(request, modulo, nivel2, submodulo):

    caminho_construido = f"{modulo}/{nivel2}/{submodulo}"
    modulos, _ = obter_modulos_dinamicos()
    
    template_escolhido = _encontrar_template_dinamico(caminho_construido)
    
    if template_escolhido:
        return render(request, template_escolhido, {
            "modulos": modulos,
            "base_url": f"/{modulo}/{nivel2}",
            "url_atual": request.path
        })
    
    return render(request, "base_sesp/home_sesp.html", {
        "modulos": modulos, 
        "modulo_em_criacao": f"{modulo} / {nivel2} / {submodulo}"
    })
import json
import math
import re
from typing import Optional, Dict, Any
import pandas as pd

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

# Importações dos seus apps
from apps.base.views import obter_modulos_dinamicos
from .models import PCAItem

# ---------------------------
# VIEW DA TELA (HTML)
# ---------------------------
def painel_pca_view(request):
    """Renderiza a página principal do PCA"""
    modulos, _ = obter_modulos_dinamicos()
    contexto = {
        'modulos': modulos,
        'base_url': '/planejamento/pca',
        'url_atual': request.path,
    }
    return render(request, "planejamento/pca/pca.html", contexto)

# ---------------------------
# HELPERS
# ---------------------------
def _clean_str(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None

_MONEY_RX = re.compile(r"[^\d,.\-]")

def _money_to_float(v):
    s = _clean_str(v)
    if not s:
        return 0.0
    s = _MONEY_RX.sub("", s)
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except:
        return 0.0

def _read_excel(file):
    return pd.read_excel(file, sheet_name="PCA", header=5)

# ---------------------------
# API: IMPORTAÇÃO
# ---------------------------
@csrf_exempt
def import_pca(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido"}, status=405)
    
    file = request.FILES.get("file")
    if not file:
        return JsonResponse({"erro": "Arquivo não enviado"}, status=400)

    df = _read_excel(file)
    df = df[df["NÚMERO DE ORDEM"].notna()].copy()

    imported = 0
    updated = 0

    for _, r in df.iterrows():
        numero_ordem = r.get("NÚMERO DE ORDEM")
        try:
            numero_ordem = int(float(numero_ordem))
        except:
            continue

        payload = {
            "numero_ordem": numero_ordem,
            "tipo_item": _clean_str(r.get("TIPO DE ITEM")),
            "descricao_objeto": _clean_str(r.get("DESCRIÇÃO SUCINTA DO OBJETO")),
            "valor_total": _clean_str(r.get("ESTIMATIVA PRELIMINAR DE VALOR TOTAL DA CONTRATAÇÃO")),
        }

        obj, created = PCAItem.objects.update_or_create(
            numero_ordem=numero_ordem,
            defaults=payload
        )

        if created:
            imported += 1
        else:
            updated += 1

    return JsonResponse({
        "importados": imported,
        "atualizados": updated,
        "total": int(df.shape[0])
    })

# ---------------------------
# API: METRICS
# ---------------------------
def pca_metrics(request):
    total = PCAItem.objects.count()
    soma = 0.0
    for v in PCAItem.objects.values_list("valor_total", flat=True):
        soma += _money_to_float(v)

    top = (
        PCAItem.objects.values("tipo_item")
        .annotate(qtd=Count("id"))
        .order_by("-qtd")[:10]
    )

    return JsonResponse({
        "total_itens": total,
        "valor_total_estimado": soma,
        "top_tipos": list(top)
    })

# ---------------------------
# API: LISTA
# ---------------------------
def pca_lista(request):
    itens = PCAItem.objects.all().order_by("numero_ordem")[:50]
    data = []
    for i in itens:
        data.append({
            "numero_ordem": i.numero_ordem,
            "tipo_item": i.tipo_item,
            "descricao_objeto": i.descricao_objeto,
            "valor_total": i.valor_total,
        })
    return JsonResponse({"itens": data})

# ---------------------------
# API: DETAIL
# ---------------------------
def pca_detail(request, numero_ordem):
    try:
        it = PCAItem.objects.get(numero_ordem=numero_ordem)
    except PCAItem.DoesNotExist:
        return JsonResponse({"erro": "Não encontrado"}, status=404)

    return JsonResponse({
        "numero_ordem": it.numero_ordem,
        "tipo_item": it.tipo_item,
        "descricao_objeto": it.descricao_objeto,
        "valor_total": it.valor_total,
    })
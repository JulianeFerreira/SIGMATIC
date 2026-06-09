from __future__ import annotations

import json
import math
import re
from typing import Optional, Dict, Any, List

import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.pca_models.pca import PCAItem

router = APIRouter(prefix="/api/pca", tags=["pca"])


# ---------------------------
# Helpers
# ---------------------------

def _clean_str(v) -> Optional[str]:
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    s = str(v).strip()
    return s if s and s.lower() != "nan" else None


_MONEY_RX = re.compile(r"[^\d,.\-]")

def _money_to_float(v) -> float:
    """
    Converte formatos comuns:
    - "R$ 1.234,56" -> 1234.56
    - "1234,56" -> 1234.56
    - "1,234.56" -> 1234.56
    Se não der, retorna 0.0
    """
    s = _clean_str(v)
    if not s:
        return 0.0
    s = _MONEY_RX.sub("", s)

    # se tem vírgula e ponto, decide pelo último separador como decimal
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            # 1.234,56 -> remove pontos e troca vírgula por ponto
            s = s.replace(".", "").replace(",", ".")
        else:
            # 1,234.56 -> remove vírgulas
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        # 1234,56 -> decimal vírgula
        s = s.replace(",", ".")
    # else: já está com ponto decimal ou inteiro

    try:
        return float(s)
    except Exception:
        return 0.0


def _read_pca_dataframe_from_excel(file_path: str) -> pd.DataFrame:
    """
    O arquivo possui cabeçalho começando na linha 6 (0-based index 5).
    """
    df = pd.read_excel(file_path, sheet_name="PCA", header=5)
    return df


def _row_to_item_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    # Campos principais
    numero_ordem = row.get("NÚMERO DE ORDEM")
    try:
        numero_ordem_int = int(float(numero_ordem)) if numero_ordem is not None else None
    except Exception:
        numero_ordem_int = None

    tipo_item = _clean_str(row.get("TIPO DE ITEM"))

    payload = {
        "numero_ordem": numero_ordem_int,
        "tipo_item": tipo_item,
        "categoria_contratacao": _clean_str(row.get("CATEGORIA DA CONTRATAÇÃO")),
        "descricao_objeto": _clean_str(row.get("DESCRIÇÃO SUCINTA DO OBJETO")),
        "justificativa": _clean_str(row.get("JUSTIFICATIVA PARA AQUISIÇÃO OU CONTRATAÇÃO")),
        "valor_unitario": _clean_str(row.get("ESTIMATIVA PRELIMINAR DE VALOR UNITÁRIO DA CONTRATAÇÃO")),
        "valor_total": _clean_str(row.get("ESTIMATIVA PRELIMINAR DE VALOR TOTAL DA CONTRATAÇÃO")),
        "grau_prioridade": _clean_str(row.get("GRAU DE PRIORIDADE DA CONTRATAÇÃO")),
        "data_pretendida": _clean_str(row.get("DATA PRETENDIDA PARA COMPRA OU CONTRATAÇÃO, A FIM DE NÃO GERAR PREJUÍZOS OU DESCONTINUIDADE DAS ATIVIDADES")),
        "municipios": _clean_str(row.get("MUNICÍPIOS CONTEMPLADOS COM A CONTRATAÇÃO ")),
        "riscos_nao_contratacao": _clean_str(row.get("RISCOS DA NÃO CONTRATAÇÃO")),
        "renovacao_contrato": _clean_str(row.get("RENOVAÇÃO DE CONTRATO")),
        "modalidade_prevista": _clean_str(row.get("MODALIDADE LICITATÓRIA PREVISTA")),
        "duracao_total": _clean_str(row.get("DURAÇÃO TOTAL DO CONTRATO OU ADITIVO")),
        "observacoes": _clean_str(row.get("OBSERVAÇÕES")),
    }

    # Guardar tudo no raw_json (para detalhe), removendo NaNs
    raw_clean = {k: _clean_str(v) for k, v in row.items()}
    payload["raw_json"] = json.dumps(raw_clean, ensure_ascii=False)

    return payload


# ---------------------------
# Importação (read-only)
# ---------------------------

@router.post("/import", summary="Importa PCA a partir de um Excel (sheet PCA)")
async def import_pca_excel(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Envie um arquivo Excel (.xlsx/.xls).")

    tmp_path = f"/tmp/{file.filename}"
    content = await file.read()
    with open(tmp_path, "wb") as f:
        f.write(content)

    try:
        df = _read_pca_dataframe_from_excel(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao ler Excel: {e}")

    # Remove linhas sem número de ordem
    df = df[df["NÚMERO DE ORDEM"].notna()].copy()

    imported = 0
    updated = 0

    # Upsert por numero_ordem
    for _, r in df.iterrows():
        row = r.to_dict()
        payload = _row_to_item_payload(row)
        if payload["numero_ordem"] is None:
            continue

        existing: Optional[PCAItem] = db.query(PCAItem).filter(PCAItem.numero_ordem == payload["numero_ordem"]).first()
        if existing:
            for k, v in payload.items():
                setattr(existing, k, v)
            updated += 1
        else:
            db.add(PCAItem(**payload))
            imported += 1

    db.commit()

    return {"importados": imported, "atualizados": updated, "total_linhas_excel": int(df.shape[0])}


# ---------------------------
# Leitura / Lista
# ---------------------------

@router.get("/metrics")
def pca_metrics(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    total = db.query(func.count(PCAItem.id)).scalar() or 0

    # soma em python porque valor_total é string com formatos variados
    valores = db.query(PCAItem.valor_total).all()
    soma = 0.0
    for (v,) in valores:
        soma += _money_to_float(v)

    # top tipos
    rows = (
        db.query(PCAItem.tipo_item, func.count(PCAItem.id).label("qtd"))
        .group_by(PCAItem.tipo_item)
        .order_by(func.count(PCAItem.id).desc())
        .limit(10)
        .all()
    )
    top_tipos = [{"tipo_item": r[0] or "Não informado", "quantidade": int(r[1] or 0)} for r in rows]

    return {"total_itens": int(total), "valor_total_estimado": float(soma), "top_tipos": top_tipos}


@router.get("/lista")
def pca_lista(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    tipo_item: Optional[str] = None,
    numero_ordem: Optional[int] = None,
    busca: Optional[str] = None,
):
    q = db.query(PCAItem)

    if numero_ordem is not None:
        q = q.filter(PCAItem.numero_ordem == numero_ordem)

    if tipo_item:
        q = q.filter(PCAItem.tipo_item.ilike(f"%{tipo_item}%"))

    if busca:
        like = f"%{busca}%"
        q = q.filter(
            (PCAItem.descricao_objeto.ilike(like))
            | (PCAItem.justificativa.ilike(like))
            | (PCAItem.observacoes.ilike(like))
        )

    total = q.with_entities(func.count(PCAItem.id)).scalar() or 0
    itens = (
        q.order_by(PCAItem.numero_ordem.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    def to_dict(it: PCAItem) -> Dict[str, Any]:
        return {
            "numero_ordem": it.numero_ordem,
            "tipo_item": it.tipo_item,
            "categoria_contratacao": it.categoria_contratacao,
            "descricao_objeto": it.descricao_objeto,
            "valor_total": it.valor_total,
            "grau_prioridade": it.grau_prioridade,
            "data_pretendida": it.data_pretendida,
        }

    return {"total": int(total), "itens": [to_dict(i) for i in itens]}


@router.get("/{numero_ordem}")
def pca_detail(
    numero_ordem: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    it: Optional[PCAItem] = db.query(PCAItem).filter(PCAItem.numero_ordem == numero_ordem).first()
    if not it:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    try:
        raw = json.loads(it.raw_json) if it.raw_json else {}
    except Exception:
        raw = {}

    return {
        "numero_ordem": it.numero_ordem,
        "tipo_item": it.tipo_item,
        "categoria_contratacao": it.categoria_contratacao,
        "descricao_objeto": it.descricao_objeto,
        "justificativa": it.justificativa,
        "valor_unitario": it.valor_unitario,
        "valor_total": it.valor_total,
        "grau_prioridade": it.grau_prioridade,
        "data_pretendida": it.data_pretendida,
        "municipios": it.municipios,
        "riscos_nao_contratacao": it.riscos_nao_contratacao,
        "renovacao_contrato": it.renovacao_contrato,
        "modalidade_prevista": it.modalidade_prevista,
        "duracao_total": it.duracao_total,
        "observacoes": it.observacoes,
        "raw": raw,
    }

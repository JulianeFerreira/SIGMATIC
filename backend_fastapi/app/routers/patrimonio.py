from __future__ import annotations

import re
from typing import Optional, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app import models

router = APIRouter(prefix="/api/planejamento", tags=["planejamento"])

SITUACAO_PLANEJAMENTO = getattr(models, "SituacaoEnum", None)
SITUACAO_PLANEJAMENTO = (
    models.SituacaoEnum.PLANEJAMENTO
    if SITUACAO_PLANEJAMENTO is not None
    else "Planejamento"
)

# --- Heurística de unidade (você pode melhorar depois) ---
_RX = re.compile(
    r"\b("
    r"Curitiba(?:\s*Centro)?|Londrina|Maring[aá]|Cascavel|Foz(?:\s*do\s*Iguaçu)?|"
    r"Ponta\s*Grossa|Guarapuava|Paranagu[aá]|UETC\s*[A-Za-zÀ-ÿ ]+|UETP\s*[A-Za-zÀ-ÿ ]+"
    r")\b",
    re.IGNORECASE
)

def unidade_estimada(descricao: Optional[str], observacao: Optional[str]) -> str:
    txt = f"{descricao or ''} {observacao or ''}".strip()
    if not txt:
        return "Não informado"
    m = _RX.search(txt)
    if not m:
        return "Não informado"
    # Normaliza um pouco
    u = m.group(1).strip()
    return re.sub(r"\s+", " ", u)


@router.get("/metrics")
def planejamento_metrics(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    q = db.query(models.Processo).filter(models.Processo.situacao == SITUACAO_PLANEJAMENTO)

    total = q.with_entities(func.count(models.Processo.id)).scalar() or 0
    valor_total = q.with_entities(func.coalesce(func.sum(models.Processo.valor_previsto), 0)).scalar() or 0

    prioritarios = (
        q.filter(
            (models.Processo.prazo_entrega_dias.isnot(None) & (models.Processo.prazo_entrega_dias <= 30))
            | (models.Processo.observacao.ilike("%prior%"))
        )
        .with_entities(func.count(models.Processo.id))
        .scalar()
        or 0
    )

    emendas = (
        q.filter(models.Processo.fonte_recurso.ilike("%emenda%"))
        .with_entities(func.count(models.Processo.id))
        .scalar()
        or 0
    )

    return {
        "total_demandas": int(total),
        "valor_planejado": float(valor_total),
        "demandas_prioritarias": int(prioritarios),
        "demandas_emenda": int(emendas),
    }


@router.get("/por_modalidade")
def planejamento_por_modalidade(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    rows = (
        db.query(models.Processo.modalidade, func.count(models.Processo.id).label("qtd"))
        .filter(models.Processo.situacao == SITUACAO_PLANEJAMENTO)
        .group_by(models.Processo.modalidade)
        .order_by(func.count(models.Processo.id).desc())
        .all()
    )
    return [{"modalidade": r[0] or "Não informado", "quantidade": int(r[1] or 0)} for r in rows]


@router.get("/por_fonte_recurso")
def planejamento_por_fonte_recurso(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    rows = (
        db.query(models.Processo.fonte_recurso, func.count(models.Processo.id).label("qtd"))
        .filter(models.Processo.situacao == SITUACAO_PLANEJAMENTO)
        .group_by(models.Processo.fonte_recurso)
        .order_by(func.count(models.Processo.id).desc())
        .all()
    )
    return [{"fonte_recurso": r[0] or "Não informado", "quantidade": int(r[1] or 0)} for r in rows]


@router.get("/por_unidade")
def planejamento_por_unidade(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    top: int = Query(10, ge=1, le=50),
):
    itens = (
        db.query(models.Processo.descricao, models.Processo.observacao)
        .filter(models.Processo.situacao == SITUACAO_PLANEJAMENTO)
        .all()
    )

    cont: Dict[str, int] = {}
    for desc, obs in itens:
        u = unidade_estimada(desc, obs)
        cont[u] = cont.get(u, 0) + 1

    # ordena desc e pega top
    ordered = sorted(cont.items(), key=lambda x: x[1], reverse=True)[:top]
    return [{"unidade": k, "quantidade": int(v)} for k, v in ordered]


@router.get("/lista")
def planejamento_lista(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    unidade: Optional[str] = None,
    busca: Optional[str] = None,
):
    q = db.query(models.Processo).filter(models.Processo.situacao == SITUACAO_PLANEJAMENTO)

    if busca:
        like = f"%{busca}%"
        q = q.filter(
            (models.Processo.numero_processo.ilike(like))
            | (models.Processo.descricao.ilike(like))
            | (models.Processo.observacao.ilike(like))
        )

    total = q.with_entities(func.count(models.Processo.id)).scalar() or 0
    itens = q.order_by(models.Processo.id.desc()).offset(skip).limit(limit).all()

    out = []
    for p in itens:
        ue = unidade_estimada(getattr(p, "descricao", None), getattr(p, "observacao", None))
        if unidade and unidade.strip():
            if unidade.strip().lower() not in ue.lower():
                continue

        out.append({
            "id": p.id,
            "numero_processo": getattr(p, "numero_processo", None),
            "descricao": getattr(p, "descricao", None),
            "unidade_estimada": ue,
            "valor_previsto": getattr(p, "valor_previsto", None),
            "modalidade": getattr(p, "modalidade", None),
            "fonte_recurso": getattr(p, "fonte_recurso", None),
            "prazo_entrega_dias": getattr(p, "prazo_entrega_dias", None),
            "data_prev_entrega": getattr(p, "data_prev_entrega", None),
            "situacao": getattr(p, "situacao", None),
            "observacao": getattr(p, "observacao", None),
        })

    return {"total": int(total), "itens": out}

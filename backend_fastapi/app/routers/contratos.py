from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import crud, schemas, models

router = APIRouter(
    prefix="/contratos",
    tags=["Contratos"]
)


# ----------------------------
# LISTAR CONTRATOS
# ----------------------------
@router.get("/", response_model=List[schemas.ContratoRead])
def listar_contratos(
    skip: int = 0,
    limit: int = 50,
    categoria_servico: Optional[str] = Query(None),
    empresa: Optional[str] = Query(None),
    local: Optional[str] = Query(None),
    status_vigencia: Optional[str] = Query(None),
    status_tramitacao: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return crud.get_contratos(
        db=db,
        skip=skip,
        limit=limit,
        categoria_servico=categoria_servico,
        empresa=empresa,
        local=local,
        status_vigencia=status_vigencia,
        status_tramitacao=status_tramitacao,
    )


# ----------------------------
# OBTER UM CONTRATO
# ----------------------------
@router.get("/{contrato_id}", response_model=schemas.ContratoRead)
def obter_contrato(contrato_id: int, db: Session = Depends(get_db)):
    contrato = crud.get_contrato(db, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato


# ----------------------------
# CRIAR CONTRATO
# ----------------------------
@router.post("/", response_model=schemas.ContratoRead)
def criar_contrato(contrato_in: schemas.ContratoCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_contrato(db, contrato_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ----------------------------
# ATUALIZAR CONTRATO
# ----------------------------
@router.put("/{contrato_id}", response_model=schemas.ContratoRead)
def atualizar_contrato(
    contrato_id: int,
    contrato_in: schemas.ContratoUpdate,
    db: Session = Depends(get_db),
):
    contrato = crud.update_contrato(db, contrato_id, contrato_in)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato


# ----------------------------
# EXCLUIR CONTRATO
# ----------------------------
@router.delete("/{contrato_id}")
def remover_contrato(contrato_id: int, db: Session = Depends(get_db)):
    sucesso = crud.delete_contrato(db, contrato_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return {"ok": True}


# ----------------------------
# MÉTRICAS DO DASHBOARD
# ----------------------------
@router.get("/dashboard/metricas")
def metricas_contratos(db: Session = Depends(get_db)):
    return crud.get_contratos_dashboard_metricas(db)

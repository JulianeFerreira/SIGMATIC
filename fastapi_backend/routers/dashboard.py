from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.security import get_current_user

from ..database import get_db
from .. import crud
from ..deps import require_role

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)]  # <-- aplica a todas as rotas
)


@router.get("/metricas")
def metricas_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal", "visualizador"])),
):
    """
    total_processos, valor_total_previsto,
    processos_finalizados, processos_tramitando, processos_atrasados
    """
    return crud.get_dashboard_metrics(db)


@router.get("/modalidade")
def distribuicao_por_modalidade(
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal", "visualizador"])),
):
    return crud.get_modalidade_distribution(db)


@router.get("/situacao")
def distribuicao_por_situacao(
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal", "visualizador"])),
):
    return crud.get_situacao_distribution(db)


@router.get("/criacao-por-mes")
def criacao_por_mes(
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal", "visualizador"])),
):
    return crud.get_criacao_por_mes(db)

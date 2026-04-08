from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import schemas, crud, models
from ..deps import require_role

router = APIRouter(
    prefix="/processos",
    tags=["processos"],
)


@router.get("/", response_model=List[schemas.ProcessoOut])
def listar_processos(
    skip: int = 0,
    limit: int = 50,
    situacao: Optional[models.SituacaoEnum] = Query(None),
    modalidade: Optional[models.ModalidadeEnum] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    unidade_atendida: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal", "visualizador"])),
):
    # conversão simples de datas (YYYY-MM-DD) se vierem
    from datetime import date

    def parse_d(d: Optional[str]):
        return date.fromisoformat(d) if d else None

    itens, total = crud.list_processos(
        db=db,
        skip=skip,
        limit=limit,
        situacao=situacao,
        modalidade=modalidade,
        data_inicio=parse_d(data_inicio),
        data_fim=parse_d(data_fim),
        valor_min=valor_min,
        valor_max=valor_max,
        unidade_atendida=unidade_atendida,
        busca=busca,
    )
    # total pode ser retornado num header, mas aqui só devolvemos os itens
    return itens


@router.get("/{processo_numero}", response_model=schemas.ProcessoDetailOut)
def obter_processo(
    processo_numero: str,
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal", "visualizador"])),
):
    proc = crud.get_processo(db, processo_numero)
    if not proc:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return proc


@router.post(
    "/", response_model=schemas.ProcessoOut, status_code=status.HTTP_201_CREATED
)
def criar_processo(
    data: schemas.ProcessoCreate,
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor"])),
):
    return crud.create_processo(db, data, usuario=user["username"])


@router.put("/{processo_numero}", response_model=schemas.ProcessoOut)
def atualizar_processo(
    processo_numero: str,
    data: schemas.ProcessoUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador", "gestor", "fiscal"])),
):
    proc = crud.get_processo(db, processo_numero)
    if not proc:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    proc = crud.update_processo(db, proc, data, usuario=user["username"])
    return proc


@router.delete("/{processo_numero}", status_code=status.HTTP_204_NO_CONTENT)
def remover_processo(
    processo_numero: str,
    db: Session = Depends(get_db),
    user=Depends(require_role(["administrador"])),
):
    proc = crud.get_processo(db, processo_numero)
    if not proc:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    crud.delete_processo(db, proc)

    @app.get("/", include_in_schema=False)
    async def dashboard_page(request: Request):
        ...

    @app.get("/ui/processos", include_in_schema=False)
    async def processos_page(request: Request):
        ...

    @app.get("/ui/processos/novo", include_in_schema=False)
    async def novo_processo_page(request: Request):
        ...

    @app.get("/ui/relatorios", include_in_schema=False)
    async def relatorios_page(request: Request):
        ...

    @app.get("/ui/processos/{processo_numero}", include_in_schema=False)
    async def processo_detail_page(request: Request, processo_numero: str):
        ...

    # Detalhes de processo
    @app.get("/ui/processos/{processo_numero}", include_in_schema=False)
    async def processo_detail_page(request: Request, processo_numero: str):
        return templates.TemplateResponse(
            "processo_detail.html",
            {"request": request, "processo_numero": processo_numero},
        )

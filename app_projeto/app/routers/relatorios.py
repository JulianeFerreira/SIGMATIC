from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io
import csv
import pandas as pd
from datetime import date, datetime

from app.database import get_db
from app import crud

router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"]
)

# -------------------------------------------------------------
# 🔎 Função auxiliar — monta filtros comuns
# -------------------------------------------------------------
def aplicar_filtros_query(query, db: Session,
                          data_inicio: date = None,
                          data_fim: date = None,
                          situacao: str = None,
                          modalidade: str = None,
                          unidade_atendida: str = None):

    if data_inicio:
        query = query.filter(crud.Processo.data_criacao >= data_inicio)

    if data_fim:
        query = query.filter(crud.Processo.data_criacao <= data_fim)

    if situacao:
        query = query.filter(crud.Processo.situacao == situacao)

    if modalidade:
        query = query.filter(crud.Processo.modalidade == modalidade)

    if unidade_atendida:
        query = query.filter(crud.Processo.unidade_atendida.ilike(f"%{unidade_atendida}%"))

    return query


# -------------------------------------------------------------
# 🧾 1) RELATÓRIO GERAL
# -------------------------------------------------------------
@router.get("/geral")
def relatorio_geral(
    data_inicio: date = None,
    data_fim: date = None,
    situacao: str = None,
    modalidade: str = None,
    unidade_atendida: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(crud.Processo)
    query = aplicar_filtros_query(query, db, data_inicio, data_fim, situacao, modalidade, unidade_atendida)
    processos = query.all()

    return processos


# -------------------------------------------------------------
# 📤 Exportar Relatório Geral (Excel / CSV)
# -------------------------------------------------------------
@router.get("/geral/export")
def relatorio_geral_export(
    formato: str = Query("excel", enum=["excel", "csv"]),
    data_inicio: date = None,
    data_fim: date = None,
    situacao: str = None,
    modalidade: str = None,
    unidade_atendida: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(crud.Processo)
    query = aplicar_filtros_query(query, db, data_inicio, data_fim, situacao, modalidade, unidade_atendida)
    processos = query.all()

    # Transformar em DataFrame
    df = pd.DataFrame([p.__dict__ for p in processos])
    df = df.drop(columns=["_sa_instance_state"], errors="ignore")

    # EXPORTAR CSV
    if formato == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, sep=";", encoding="utf-8")
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=relatorio_geral.csv"}
        )

    # EXPORTAR EXCEL
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=relatorio_geral.xlsx"}
    )


# -------------------------------------------------------------
# ⏰ 2) PROCESSOS EM ATRASO
# -------------------------------------------------------------
@router.get("/atraso")
def relatorio_atraso(db: Session = Depends(get_db)):
    return crud.get_processos_em_atraso(db)


# 📤 EXPORTAR EM ATRASO
@router.get("/atraso/export")
def relatorio_atraso_export(
    formato: str = Query("excel", enum=["excel", "csv"]),
    db: Session = Depends(get_db)
):
    processos = crud.get_processos_em_atraso(db)

    df = pd.DataFrame([p.__dict__ for p in processos])
    df = df.drop(columns=["_sa_instance_state"], errors="ignore")

    if formato == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, sep=";", encoding="utf-8")
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=processos_atraso.csv"}
        )

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=processos_atraso.xlsx"}
    )


# -------------------------------------------------------------
# 💰 3) RELATÓRIO FINANCEIRO — valor por modalidade + período
# -------------------------------------------------------------
@router.get("/financeiro")
def relatorio_financeiro(
    data_inicio: date = None,
    data_fim: date = None,
    db: Session = Depends(get_db)
):
    query = db.query(crud.Processo)
    query = aplicar_filtros_query(query, db, data_inicio, data_fim)

    processos = query.all()

    # Soma por modalidade
    modalidades = {}
    for p in processos:
        modalidades.setdefault(p.modalidade, 0)
        modalidades[p.modalidade] += float(p.valor_previsto or 0)

    # Evolução mensal
    meses = {}
    for p in processos:
        mes = datetime.strptime(p.data_criacao, "%Y-%m-%d").strftime("%Y-%m")
        meses.setdefault(mes, 0)
        meses[mes] += float(p.valor_previsto or 0)

    return {
        "valor_por_modalidade": modalidades,
        "evolucao_mensal": meses
    }


# -------------------------------------------------------------
# 👨‍💼 4) PERFORMANCE POR GESTOR
# -------------------------------------------------------------
@router.get("/gestor")
def relatorio_por_gestor(db: Session = Depends(get_db)):
    query = db.query(crud.Processo)
    processos = query.all()

    gestores = {}

    for p in processos:
        gestor = p.gestor or "Não informado"
        gestores.setdefault(gestor, {
            "total_processos": 0,
            "processos_finalizados": 0,
            "tempo_medio_dias": 0,
            "amostras": []
        })
        gestores[gestor]["total_processos"] += 1


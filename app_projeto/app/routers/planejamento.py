from __future__ import annotations

from collections import Counter
from datetime import datetime, date
from typing import Any

import math
import pandas as pd
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from sqlalchemy import text

from app.database import engine

router = APIRouter(prefix="/api", tags=["planejamento"])


# ============================================================
# Helpers
# ============================================================

def _safe_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return 0.0
    s = s.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return 0.0


def _to_date(value: Any) -> date | None:
    if value is None or str(value).strip() == "":
        return None
    if isinstance(value, date):
        return value
    s = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            continue
    return None


def _normalize_text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_status(row: dict[str, Any]) -> str:
    status = _normalize_text(row.get("status") or row.get("situacao") or row.get("onde_esta")).lower()
    if status:
        if any(k in status for k in ["conclu", "entregue", "finalizado", "homologado", "contratado"]):
            return "concluido"
        if any(k in status for k in ["atras", "parado", "pend", "devolvido"]):
            return "atrasado"
        if any(k in status for k in ["andamento", "preg", "licit", "execu", "tramit", "instru"]):
            return "em_execucao"
        if any(k in status for k in ["planej", "estudo", "dfd", "etp"]):
            return "planejado"
    prazo = _to_date(row.get("data_prevista") or row.get("data_prevista_entrega") or row.get("data_pregao"))
    if prazo and prazo < date.today():
        return "atrasado"
    return "planejado"


def _extract_unidade(row: dict[str, Any]) -> str:
    return (
        _normalize_text(row.get("unidade_estimada"))
        or _normalize_text(row.get("unidade_atendida"))
        or _normalize_text(row.get("unidade_pcp"))
        or "Não informado"
    )


def _extract_tipo(row: dict[str, Any]) -> str:
    return _normalize_text(row.get("tipo_item") or row.get("categoria_contratacao") or row.get("modalidade") or "Não informado")


def _extract_mes(row: dict[str, Any]) -> str:
    dt = _to_date(row.get("data_pretendida") or row.get("data_prevista_entrega") or row.get("data_pregao"))
    if not dt:
        return "Não informado"
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    return meses[dt.month - 1]


def _fetch_planejamento_rows() -> list[dict[str, Any]]:
    with engine.begin() as conn:
        rows = conn.execute(text(
            """
            SELECT
                processo_numero AS numero_processo,
                descricao,
                unidade_pcp,
                unidade_atendida,
                valor_previsto,
                fonte_recurso,
                modalidade,
                data_pregao,
                prazo_entrega_dias,
                data_prevista_entrega,
                situacao,
                observacao,
                observacoes_adicionais,
                obs_extras,
                convenio
            FROM processos
            ORDER BY processo_numero DESC
            """
        )).mappings().all()
    return [dict(r) for r in rows]


def _ensure_pca_table() -> None:
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS pca_itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_ordem TEXT NOT NULL UNIQUE,
                tipo_item TEXT,
                categoria_contratacao TEXT,
                descricao_objeto TEXT,
                justificativa TEXT,
                riscos_nao_contratacao TEXT,
                municipios TEXT,
                valor_unitario TEXT,
                valor_total TEXT,
                grau_prioridade TEXT,
                data_pretendida TEXT,
                modalidade_prevista TEXT,
                duracao_total TEXT,
                observacoes TEXT,
                criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        ))


# ============================================================
# Planejamento dashboard
# ============================================================

@router.get("/planejamento/metrics")
def planejamento_metrics():
    rows = _fetch_planejamento_rows()
    total = len(rows)
    valor_planejado = sum(_safe_float(r.get("valor_previsto")) for r in rows)

    normalized = [_normalize_status(r) for r in rows]
    em_execucao = sum(1 for s in normalized if s == "em_execucao")
    concluidos = sum(1 for s in normalized if s == "concluido")
    atrasados = sum(1 for s in normalized if s == "atrasado")
    planejados = sum(1 for s in normalized if s == "planejado")

    prioritarias = sum(
        1 for r in rows
        if any(k in _normalize_text(r.get("observacao") or r.get("observacoes_adicionais") or "").lower() for k in ["prior", "urg", "imediat"])
    )
    emenda = sum(1 for r in rows if _normalize_text(r.get("convenio")))
    execucao_percentual = round(((em_execucao + concluidos) / total) * 100, 1) if total else 0

    return {
        "total_demandas": total,
        "valor_planejado": valor_planejado,
        "demandas_prioritarias": prioritarias,
        "demandas_emenda": emenda,
        "planejados": planejados,
        "em_execucao": em_execucao,
        "concluidos": concluidos,
        "atrasados": atrasados,
        "execucao_percentual": execucao_percentual,
    }


@router.get("/planejamento/por_unidade")
def planejamento_por_unidade(top: int = 10):
    rows = _fetch_planejamento_rows()
    counter = Counter(_extract_unidade(r) for r in rows)
    return [{"unidade": k, "quantidade": v} for k, v in counter.most_common(top)]


@router.get("/planejamento/por_modalidade")
def planejamento_por_modalidade():
    rows = _fetch_planejamento_rows()
    counter = Counter(_normalize_text(r.get("modalidade") or "Não informado") for r in rows)
    return [{"modalidade": k, "quantidade": v} for k, v in counter.most_common()]


@router.get("/planejamento/por_fonte_recurso")
def planejamento_por_fonte_recurso():
    rows = _fetch_planejamento_rows()
    counter = Counter(_normalize_text(r.get("fonte_recurso") or "Não informado") for r in rows)
    return [{"fonte_recurso": k, "quantidade": v} for k, v in counter.most_common()]


@router.get("/planejamento/por_mes")
def planejamento_por_mes():
    rows = _fetch_planejamento_rows()
    ordem = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez", "Não informado"]
    counter = Counter(_extract_mes(r) for r in rows)
    return [{"mes": m, "quantidade": counter.get(m, 0)} for m in ordem if counter.get(m, 0) > 0 or m != "Não informado"]


@router.get("/planejamento/top_tipos")
def planejamento_top_tipos(top: int = 8):
    rows = _fetch_planejamento_rows()
    counter = Counter(_extract_tipo(r) for r in rows)
    return [{"tipo": k, "quantidade": v} for k, v in counter.most_common(top)]


@router.get("/planejamento/alertas")
def planejamento_alertas(limit: int = 8):
    rows = _fetch_planejamento_rows()
    alertas: list[dict[str, Any]] = []
    hoje = date.today()
    for r in rows:
        status = _normalize_status(r)
        prazo = _to_date(r.get("data_prevista_entrega") or r.get("data_pregao"))
        dias = None
        if prazo:
            dias = (prazo - hoje).days
        if status == "atrasado":
            alertas.append({
                "tipo": "atrasado",
                "processo": r.get("numero_processo"),
                "descricao": r.get("descricao"),
                "mensagem": f"Processo {r.get('numero_processo')} com indício de atraso.",
                "dias": dias,
            })
        elif dias is not None and dias <= 30:
            alertas.append({
                "tipo": "atencao",
                "processo": r.get("numero_processo"),
                "descricao": r.get("descricao"),
                "mensagem": f"Processo {r.get('numero_processo')} com marco próximo ({dias} dias).",
                "dias": dias,
            })
    prioridade = {"atrasado": 0, "atencao": 1}
    alertas.sort(key=lambda x: (prioridade.get(x["tipo"], 9), 999999 if x["dias"] is None else x["dias"]))
    return alertas[:limit]


@router.get("/planejamento/lista")
def planejamento_lista(
    skip: int = 0,
    limit: int = 20,
    unidade: str | None = None,
    busca: str | None = None,
    status: str | None = None,
):
    rows = _fetch_planejamento_rows()

    itens = []
    for r in rows:
        item = {
            "numero_processo": r.get("numero_processo"),
            "descricao": r.get("descricao"),
            "unidade_estimada": _extract_unidade(r),
            "modalidade": _normalize_text(r.get("modalidade") or "Não informado"),
            "fonte_recurso": _normalize_text(r.get("fonte_recurso") or "Não informado"),
            "valor_previsto": _safe_float(r.get("valor_previsto")),
            "prazo_entrega_dias": r.get("prazo_entrega_dias"),
            "status": _normalize_status(r),
            "observacao": " | ".join(filter(None, [
                _normalize_text(r.get("observacao")),
                _normalize_text(r.get("observacoes_adicionais")),
                _normalize_text(r.get("obs_extras")),
            ])),
        }
        itens.append(item)

    if unidade:
        u = unidade.lower().strip()
        itens = [x for x in itens if u in (x.get("unidade_estimada") or "").lower()]
    if busca:
        b = busca.lower().strip()
        itens = [x for x in itens if b in " ".join([
            str(x.get("numero_processo") or ""),
            str(x.get("descricao") or ""),
            str(x.get("observacao") or ""),
            str(x.get("modalidade") or ""),
        ]).lower()]
    if status:
        s = status.lower().strip()
        itens = [x for x in itens if x.get("status") == s]

    total = len(itens)
    return {"total": total, "itens": itens[skip: skip + limit]}


# ============================================================
# PCA endpoints
# ============================================================

@router.get("/pca/metrics")
def pca_metrics():
    _ensure_pca_table()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT tipo_item, valor_total FROM pca_itens")).mappings().all()
    rows = [dict(r) for r in rows]
    total_itens = len(rows)
    valor_total_estimado = sum(_safe_float(r.get("valor_total")) for r in rows)
    top_tipos = [{"tipo_item": k, "quantidade": v} for k, v in Counter(_normalize_text(r.get("tipo_item") or "Não informado") for r in rows).most_common(5)]
    return {
        "total_itens": total_itens,
        "valor_total_estimado": valor_total_estimado,
        "top_tipos": top_tipos,
    }


@router.get("/pca/lista")
def pca_lista(
    skip: int = 0,
    limit: int = 50,
    numero_ordem: str | None = None,
    tipo_item: str | None = None,
    busca: str | None = None,
):
    _ensure_pca_table()
    where = []
    params: dict[str, Any] = {}
    if numero_ordem:
        where.append("numero_ordem = :numero_ordem")
        params["numero_ordem"] = numero_ordem
    if tipo_item:
        where.append("LOWER(tipo_item) LIKE :tipo_item")
        params["tipo_item"] = f"%{tipo_item.lower()}%"
    if busca:
        where.append("(" + " OR ".join([
            "LOWER(COALESCE(tipo_item,'')) LIKE :busca",
            "LOWER(COALESCE(categoria_contratacao,'')) LIKE :busca",
            "LOWER(COALESCE(descricao_objeto,'')) LIKE :busca",
            "LOWER(COALESCE(justificativa,'')) LIKE :busca",
            "LOWER(COALESCE(observacoes,'')) LIKE :busca",
        ]) + ")")
        params["busca"] = f"%{busca.lower()}%"

    clause = (" WHERE " + " AND ".join(where)) if where else ""

    with engine.begin() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM pca_itens{clause}"), params).scalar() or 0
        rows = conn.execute(text(
            f"""
            SELECT numero_ordem, tipo_item, categoria_contratacao, descricao_objeto,
                   valor_total, grau_prioridade, data_pretendida
            FROM pca_itens
            {clause}
            ORDER BY CAST(numero_ordem AS INTEGER)
            LIMIT :limit OFFSET :skip
            """
        ), {**params, "limit": limit, "skip": skip}).mappings().all()

    return {"total": int(total), "itens": [dict(r) for r in rows]}


@router.get("/pca/{numero_ordem}")
def pca_detail(numero_ordem: str):
    _ensure_pca_table()
    with engine.begin() as conn:
        row = conn.execute(text("SELECT * FROM pca_itens WHERE numero_ordem = :n"), {"n": numero_ordem}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Item do PCA não encontrado.")
    return dict(row)


@router.post("/pca/import")
def pca_import(file: UploadFile = File(...)):
    _ensure_pca_table()
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Envie um arquivo Excel (.xlsx ou .xls).")

    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao ler Excel: {e}")

    original_cols = {str(c).strip().lower(): c for c in df.columns}

    def find_col(*options: str):
        for op in options:
            if op.lower() in original_cols:
                return original_cols[op.lower()]
        return None

    c_numero = find_col("Número de Ordem", "Numero de Ordem", "Nº de Ordem", "No de Ordem")
    c_tipo = find_col("Tipo de Item")
    c_categoria = find_col("Categoria", "Categoria de Contratação", "Categoria da Contratação")
    c_descricao = find_col("Descrição sucinta", "Descrição do Objeto", "Descricao do Objeto", "Objeto")
    c_just = find_col("Justificativa")
    c_riscos = find_col("Riscos da Não Contratação", "Riscos da Nao Contratacao")
    c_municipios = find_col("Municípios", "Municipios")
    c_vu = find_col("Valor unitário", "Valor Unitário", "Valor unitario")
    c_vt = find_col("Valor total", "Valor Total")
    c_prio = find_col("Grau de prioridade", "Prioridade")
    c_data = find_col("Data pretendida", "Data Pretendida")
    c_modalidade = find_col("Modalidade prevista", "Modalidade Prevista")
    c_duracao = find_col("Duração total", "Duracao total", "Duração")
    c_obs = find_col("Observações", "Observacoes")

    if not c_numero:
        raise HTTPException(status_code=400, detail="Não encontrei a coluna 'Número de Ordem' no Excel.")

    total_linhas_excel = len(df)
    importados = 0
    atualizados = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            numero_ordem = _normalize_text(row.get(c_numero))
            if not numero_ordem or numero_ordem.lower() == "nan":
                continue
            payload = {
                "numero_ordem": numero_ordem,
                "tipo_item": _normalize_text(row.get(c_tipo)) if c_tipo else "",
                "categoria_contratacao": _normalize_text(row.get(c_categoria)) if c_categoria else "",
                "descricao_objeto": _normalize_text(row.get(c_descricao)) if c_descricao else "",
                "justificativa": _normalize_text(row.get(c_just)) if c_just else "",
                "riscos_nao_contratacao": _normalize_text(row.get(c_riscos)) if c_riscos else "",
                "municipios": _normalize_text(row.get(c_municipios)) if c_municipios else "",
                "valor_unitario": _normalize_text(row.get(c_vu)) if c_vu else "",
                "valor_total": _normalize_text(row.get(c_vt)) if c_vt else "",
                "grau_prioridade": _normalize_text(row.get(c_prio)) if c_prio else "",
                "data_pretendida": _normalize_text(row.get(c_data)) if c_data else "",
                "modalidade_prevista": _normalize_text(row.get(c_modalidade)) if c_modalidade else "",
                "duracao_total": _normalize_text(row.get(c_duracao)) if c_duracao else "",
                "observacoes": _normalize_text(row.get(c_obs)) if c_obs else "",
            }
            exists = conn.execute(text("SELECT id FROM pca_itens WHERE numero_ordem = :numero_ordem"), {"numero_ordem": numero_ordem}).first()
            if exists:
                conn.execute(text(
                    """
                    UPDATE pca_itens
                       SET tipo_item = :tipo_item,
                           categoria_contratacao = :categoria_contratacao,
                           descricao_objeto = :descricao_objeto,
                           justificativa = :justificativa,
                           riscos_nao_contratacao = :riscos_nao_contratacao,
                           municipios = :municipios,
                           valor_unitario = :valor_unitario,
                           valor_total = :valor_total,
                           grau_prioridade = :grau_prioridade,
                           data_pretendida = :data_pretendida,
                           modalidade_prevista = :modalidade_prevista,
                           duracao_total = :duracao_total,
                           observacoes = :observacoes,
                           atualizado_em = CURRENT_TIMESTAMP
                     WHERE numero_ordem = :numero_ordem
                    """
                ), payload)
                atualizados += 1
            else:
                conn.execute(text(
                    """
                    INSERT INTO pca_itens (
                        numero_ordem, tipo_item, categoria_contratacao, descricao_objeto,
                        justificativa, riscos_nao_contratacao, municipios, valor_unitario,
                        valor_total, grau_prioridade, data_pretendida, modalidade_prevista,
                        duracao_total, observacoes
                    ) VALUES (
                        :numero_ordem, :tipo_item, :categoria_contratacao, :descricao_objeto,
                        :justificativa, :riscos_nao_contratacao, :municipios, :valor_unitario,
                        :valor_total, :grau_prioridade, :data_pretendida, :modalidade_prevista,
                        :duracao_total, :observacoes
                    )
                    """
                ), payload)
                importados += 1

    return {
        "importados": importados,
        "atualizados": atualizados,
        "total_linhas_excel": total_linhas_excel,
    }

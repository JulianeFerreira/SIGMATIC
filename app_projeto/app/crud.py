from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from . import models, schemas
#############################################################################################
#Autenticação
from app.core.security import hash_password
#############################################################################################

def create_processo(db: Session, data: schemas.ProcessoCreate, usuario: str = None):
    obj = models.Processo(**data.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_processo(db: Session, processo_numero: str) -> Optional[models.Processo]:
    return db.query(models.Processo).filter(
        models.Processo.processo_numero == processo_numero
    ).first()


def list_processos(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    situacao: Optional[models.SituacaoEnum] = None,
    modalidade: Optional[models.ModalidadeEnum] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    valor_min: Optional[float] = None,
    valor_max: Optional[float] = None,
    unidade_atendida: Optional[str] = None,
    busca: Optional[str] = None,
):
    query = db.query(models.Processo)

    if situacao:
        query = query.filter(models.Processo.situacao == situacao)
    if modalidade:
        query = query.filter(models.Processo.modalidade == modalidade)
    if data_inicio:
        query = query.filter(models.Processo.data_criacao >= data_inicio)
    if data_fim:
        query = query.filter(models.Processo.data_criacao <= data_fim)
    if valor_min is not None:
        query = query.filter(models.Processo.valor_previsto >= valor_min)
    if valor_max is not None:
        query = query.filter(models.Processo.valor_previsto <= valor_max)
    if unidade_atendida:
        query = query.filter(
            models.Processo.unidade_atendida.ilike(f"%{unidade_atendida}%")
        )
    if busca:
        like = f"%{busca}%"
        query = query.filter(
            (
                models.Processo.processo_numero.ilike(like)
                | models.Processo.descricao.ilike(like)
                | models.Processo.gestor.ilike(like)
                | models.Processo.fiscal.ilike(like)
            )
        )

    total = query.count()
    itens = query.order_by(models.Processo.data_criacao.desc()).offset(skip).limit(
        limit
    ).all()
    return itens, total


def _registrar_auditoria(
    db: Session,
    processo: models.Processo,
    campo: str,
    valor_antigo,
    valor_novo,
    usuario: Optional[str],
):
    if str(valor_antigo) == str(valor_novo):
        return
    log = models.AuditLog(
        processo_numero=processo.processo_numero,
        campo=campo,
        valor_antigo=str(valor_antigo) if valor_antigo is not None else None,
        valor_novo=str(valor_novo) if valor_novo is not None else None,
        usuario=usuario,
    )
    db.add(log)


def update_processo(
    db: Session,
    processo: models.Processo,
    data: schemas.ProcessoUpdate,
    usuario: str = None,
):
    dados = data.dict(exclude_unset=True)
    campos_auditar = {"situacao", "valor_previsto", "observacao"}

    for campo, novo in dados.items():
        antigo = getattr(processo, campo)
        setattr(processo, campo, novo)

        if campo in campos_auditar:
            _registrar_auditoria(db, processo, campo, antigo, novo, usuario)

    db.add(processo)
    db.commit()
    db.refresh(processo)
    return processo


def delete_processo(db: Session, processo: models.Processo):
    db.delete(processo)
    db.commit()


# ---------- MÉTRICAS PARA DASHBOARD ----------

from datetime import date
from sqlalchemy import func
from . import models

def get_dashboard_metrics(db: Session):
    total_processos = db.query(func.count(models.Processo.processo_numero)).scalar()
    valor_total_previsto = db.query(func.coalesce(func.sum(models.Processo.valor_previsto), 0)).scalar()

    processos_finalizados = db.query(func.count(models.Processo.processo_numero)).filter(
        models.Processo.situacao == models.SituacaoEnum.FINALIZADO
    ).scalar()

    processos_tramitando = db.query(func.count(models.Processo.processo_numero)).filter(
        models.Processo.situacao == models.SituacaoEnum.TRAMITANDO
    ).scalar()

    processos_arquivados = db.query(func.count(models.Processo.processo_numero)).filter(
        models.Processo.situacao == models.SituacaoEnum.ARQUIVADO
    ).scalar()

    hoje = date.today()
    processos_atrasados = (
        db.query(func.count(models.Processo.processo_numero))
        .filter(
            models.Processo.data_prevista_entrega < hoje,
            models.Processo.material_entregue.is_(None),
        )
        .scalar()
    )

    return {
        "total_processos": total_processos or 0,
        "valor_total_previsto": float(valor_total_previsto or 0),
        "processos_finalizados": processos_finalizados or 0,
        "processos_tramitando": processos_tramitando or 0,
        "processos_arquivados": processos_arquivados or 0,
        "processos_atrasados": processos_atrasados or 0,
    }


def get_modalidade_distribution(db: Session):
    rows = (
        db.query(models.Processo.modalidade, func.count(models.Processo.processo_numero))
        .group_by(models.Processo.modalidade)
        .all()
    )
    return [{"modalidade": r[0].value, "quantidade": r[1]} for r in rows]


def get_situacao_distribution(db: Session):
    rows = (
        db.query(models.Processo.situacao, func.count(models.Processo.processo_numero))
        .group_by(models.Processo.situacao)
        .all()
    )
    return [{"situacao": r[0].value, "quantidade": r[1]} for r in rows]


def get_criacao_por_mes(db: Session):
    rows = (
        db.query(
            func.strftime("%Y-%m", models.Processo.data_criacao),
            func.count(models.Processo.processo_numero),
        )
        .group_by(func.strftime("%Y-%m", models.Processo.data_criacao))
        .order_by(func.strftime("%Y-%m", models.Processo.data_criacao))
        .all()
    )
    return [{"mes": r[0], "quantidade": r[1]} for r in rows]


def get_processos_em_atraso(db: Session):
    hoje = date.today()
    return (
        db.query(models.Processo)
        .filter(
            models.Processo.data_prevista_entrega < hoje,
            models.Processo.material_entregue.is_(None),
        )
        .all()
    )


def get_performance_por_gestor(db: Session):
    # total_processos, processos_finalizados
    rows = (
        db.query(
            models.Processo.gestor,
            func.count(models.Processo.processo_numero).label("total"),
            func.sum(
                func.case(
                    (models.Processo.situacao == models.SituacaoEnum.FINALIZADO, 1),
                    else_=0,
                )
            ).label("finalizados"),
        )
        .group_by(models.Processo.gestor)
        .all()
    )
    # tempo_medio aqui é placeholder (precisa mais dados de histórico)
    return [
        {
            "gestor": r[0],
            "total_processos": r[1],
            "processos_finalizados": r[2],
            "tempo_medio": None,
        }
        for r in rows
        if r[0]
    ]

from sqlalchemy import func

def get_contratos_dashboard_metricas(db: Session):
    """
    Retorna métricas para o dashboard de contratos.
    """
    # Totais por status de vigência
    total_contratos = db.query(func.count(models.Contrato.id)).scalar() or 0

    def count_vigencia(status: str) -> int:
        if not status:
            return 0
        return (
            db.query(func.count(models.Contrato.id))
            .filter(models.Contrato.status_vigencia == status)
            .scalar()
            or 0
        )

    vigentes = count_vigencia("vigente")
    proximo_vencimento = count_vigencia("proximo_vencimento")
    vencidos = count_vigencia("vencido")
    prorrogados = count_vigencia("prorrogado")
    rescindidos = count_vigencia("rescindido")

    # Distribuição por categoria de serviço
    rows_cat = (
        db.query(models.Contrato.categoria_servico, func.count(models.Contrato.id))
        .group_by(models.Contrato.categoria_servico)
        .all()
    )
    por_categoria = [
        {"categoria": r[0], "quantidade": r[1]}
        for r in rows_cat
        if r[0] is not None
    ]

    # Distribuição por status de tramitação
    rows_status = (
        db.query(models.Contrato.status_tramitacao, func.count(models.Contrato.id))
        .group_by(models.Contrato.status_tramitacao)
        .all()
    )
    por_status_tramitacao = [
        {"status": r[0], "quantidade": r[1]}
        for r in rows_status
        if r[0] is not None
    ]

    return {
        "total_contratos": total_contratos,
        "vigentes": vigentes,
        "proximo_vencimento": proximo_vencimento,
        "vencidos": vencidos,
        "prorrogados": prorrogados,
        "rescindidos": rescindidos,
        "por_categoria": por_categoria,
        "por_status_tramitacao": por_status_tramitacao,
    }

#####################################################################
# LOGIN / USUÁRIOS
#####################################################################
from sqlalchemy import or_
from app.core.security import hash_password


def create_user(db: Session, data: dict):
    """
    Espera receber um dict com:
      - username (ou login)
      - email
      - full_name (opcional)
      - password (senha em texto - só para gerar o hash)
    """
    print("🟢 Dados recebidos:", data)

    username = data.get("username") or data.get("login") or data.get("email")
    email = data.get("email") or username
    full_name = data.get("full_name") or data.get("name") or ""

    if not username or not email or not data.get("password"):
        raise ValueError("Campos obrigatórios: username/email e password")

    hashed = hash_password(data["password"])

    # IMPORTANTE:
    # - `password` no DB pode ser NOT NULL (legado). Preenchemos com 'LEGACY'
    # - a validação do login deve usar `hashed_password`
    user = models.User(
        username=username,
        email=email,
        full_name=full_name,
        password="LEGACY",
        hashed_password=hashed,
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_login(db: Session, login: str):
    """
    Aceita login por username OU email.
    """
    return (
        db.query(models.User)
        .filter(or_(models.User.username == login, models.User.email == login))
        .first()
    )

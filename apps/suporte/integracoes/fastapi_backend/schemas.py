from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel
from pydantic import ConfigDict
from .models import FonteRecursoEnum, ModalidadeEnum, SituacaoEnum


# ============================================================
#  PROCESSOS DE COMPRAS
# ============================================================

class ProcessoBase(BaseModel):
    # Configuração Pydantic v2: aceita enums externas e usa seus valores
    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    descricao: str
    instrucao_responsavel: Optional[str] = None
    unidade_pcp: Optional[str] = None
    unidade_atendida: str
    data_criacao: date

    valor_previsto: Decimal
    fonte_recurso: FonteRecursoEnum
    modalidade: ModalidadeEnum

    data_pregao: Optional[date] = None
    contrato_assinado: Optional[date] = None
    empenho_assinado: Optional[date] = None
    empenho_contrato_enviado: Optional[date] = None

    prazo_entrega_dias: Optional[int] = None
    data_prevista_entrega: Optional[date] = None
    cobrado_entrega_dia: Optional[date] = None
    material_entregue: Optional[date] = None

    convenio: Optional[str] = None

    situacao: SituacaoEnum = SituacaoEnum.TRAMITANDO

    observacao: Optional[str] = None
    gestor: Optional[str] = None
    fiscal: Optional[str] = None

    onde_esta: Optional[str] = None
    desde_consulta: Optional[date] = None

    observacoes_adicionais: Optional[str] = None
    obs_extras: Optional[str] = None


class ProcessoCreate(ProcessoBase):
    processo_numero: str


class ProcessoUpdate(BaseModel):
    # Configuração também aqui, pois usa Enums opcionais
    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    # todos opcionais para PATCH/PUT
    descricao: Optional[str] = None
    instrucao_responsavel: Optional[str] = None
    unidade_pcp: Optional[str] = None
    unidade_atendida: Optional[str] = None
    data_criacao: Optional[date] = None

    valor_previsto: Optional[Decimal] = None
    fonte_recurso: Optional[FonteRecursoEnum] = None
    modalidade: Optional[ModalidadeEnum] = None

    data_pregao: Optional[date] = None
    contrato_assinado: Optional[date] = None
    empenho_assinado: Optional[date] = None
    empenho_contrato_enviado: Optional[date] = None

    prazo_entrega_dias: Optional[int] = None
    data_prevista_entrega: Optional[date] = None
    cobrado_entrega_dia: Optional[date] = None
    material_entregue: Optional[date] = None

    convenio: Optional[str] = None
    situacao: Optional[SituacaoEnum] = None

    observacao: Optional[str] = None
    gestor: Optional[str] = None
    fiscal: Optional[str] = None

    onde_esta: Optional[str] = None
    desde_consulta: Optional[date] = None

    observacoes_adicionais: Optional[str] = None
    obs_extras: Optional[str] = None


class ProcessoOut(ProcessoBase):
    processo_numero: str

    # from_attributes para funcionar com ORM + enums como valores
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )


# ============================================================
#  AUDITORIA
# ============================================================

class AuditLogOut(BaseModel):
    id: int
    processo_numero: str
    campo: str
    valor_antigo: Optional[str]
    valor_novo: Optional[str]
    data: datetime
    usuario: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class ProcessoDetailOut(ProcessoOut):
    auditorias: List[AuditLogOut] = []


# ============================================================
#  CONTRATOS
# ============================================================

class ContratoBase(BaseModel):
    gms: str
    numero_contrato: str
    empresa: str
    categoria_servico: str
    local: str
    quantidade: Optional[str] = None
    posto: Optional[str] = None

    data_inicio: date
    data_termino: date

    status_vigencia: Optional[str] = None
    status_tramitacao: Optional[str] = None
    status_financeiro: Optional[str] = None

    status_ta: Optional[str] = None
    observacoes_ta: Optional[str] = None

    status_tap: Optional[str] = None
    ano_reajuste: Optional[str] = None

    numero_protocolo: Optional[str] = None
    descricao_tramitacao: Optional[str] = None
    localizacao_documento: Optional[str] = None
    data_tramitacao: Optional[date] = None

    observacoes_gerais: Optional[str] = None
    historico_alteracoes: Optional[str] = None


class ContratoCreate(ContratoBase):
    pass


class ContratoUpdate(BaseModel):
    gms: Optional[str] = None
    numero_contrato: Optional[str] = None
    empresa: Optional[str] = None
    categoria_servico: Optional[str] = None
    local: Optional[str] = None
    quantidade: Optional[str] = None
    posto: Optional[str] = None

    data_inicio: Optional[date] = None
    data_termino: Optional[date] = None

    status_vigencia: Optional[str] = None
    status_tramitacao: Optional[str] = None
    status_financeiro: Optional[str] = None

    status_ta: Optional[str] = None
    observacoes_ta: Optional[str] = None

    status_tap: Optional[str] = None
    ano_reajuste: Optional[str] = None

    numero_protocolo: Optional[str] = None
    descricao_tramitacao: Optional[str] = None
    localizacao_documento: Optional[str] = None
    data_tramitacao: Optional[date] = None

    observacoes_gerais: Optional[str] = None
    historico_alteracoes: Optional[str] = None


class ContratoRead(ContratoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ============================================================
#  ENUMS USADAS NO SISTEMA (COMPATÍVEIS COM PYDANTIC V2)
# ============================================================

class FonteRecursoEnum(str, Enum):
    RECURSOS_PROPRIOS = "Recursos próprios"
    CONVENIO = "Convênio"
    EMENDA_PARLAMENTAR = "Emenda parlamentar"
    OUTROS = "Outros"


class ModalidadeEnum(str, Enum):
    DISPENSA = "Dispensa"
    INEXIGIBILIDADE = "Inexigibilidade"
    PREGAO_ELETRONICO = "Pregão eletrônico"
    CONCORRENCIA = "Concorrência"
    CHAMAMENTO_PUBLICO = "Chamamento público"
    OUTRA = "Outra"


class SituacaoEnum(str, Enum):
    TRAMITANDO = "Tramitando"
    PLANEJAMENTO = "Planejamento"
    EM_ANDAMENTO = "Em andamento"
    CONCLUIDO = "Concluído"
    CANCELADO = "Cancelado"
    SUSPENSO = "Suspenso"


# ============================================================
#  MODELO DE USUÁRIOS (LOGIN)
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


# ============================================================
#  PROCESSOS DE COMPRAS (TABELA MIGRADA DA PLANILHA)
# ============================================================

class ProcessoCompra(Base):
    __tablename__ = "processos_compras"

    id = Column(Integer, primary_key=True, index=True)

    numero_processo = Column(String, index=True)              # PROCESSO N°
    descricao = Column(String)                                # DESCRIÇÃO
    data_criacao = Column(String)                             # DATA DE CRIAÇÃO
    valor_previsto = Column(Float)                            # VALOR PREVISTO
    fonte_recurso = Column(String)                            # FONTE DE RECURSO
    modalidade = Column(String)                               # MODALIDADE
    data_pregao = Column(String)                              # DATA DO PREGÃO
    contrato_assinado = Column(String)                        # CONTRATO ASSINADO
    empenho_assinado = Column(String)                         # EMPENHO ASSINADO
    empenho_enviado_fornecedor = Column(String)               # EMPENHO E CONTRATO ENVIADO AO FORNECEDOR (DATA)
    prazo_entrega_dias = Column(Integer)                      # PRAZO DE ENTREGA (DIAS)
    data_prev_entrega = Column(String)                        # DATA PREV. DE ENTREGA
    cobrado_entrega_dia = Column(String)                      # COBRADO ENTREGA NO DIA
    material_entregue_data = Column(String)                   # MATERIAL ENTREGUE (DATA)
    situacao = Column(String)                                 # SITUAÇÃO
    observacao = Column(String)                               # OBSERVAÇÃO


# ============================================================
#  ALIAS PARA COMPATIBILIDADE COM CÓDIGO EXISTENTE
# ============================================================

Processo = ProcessoCompra

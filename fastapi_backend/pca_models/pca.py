from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database import Base


class PCAItem(Base):
    __tablename__ = "pca_itens"

    id = Column(Integer, primary_key=True, index=True)

    # Colunas principais (para navegação/consulta)
    numero_ordem = Column(Integer, index=True, unique=True, nullable=False)
    tipo_item = Column(String, index=True, nullable=True)

    # Colunas úteis (read-only, vêm do Excel)
    categoria_contratacao = Column(String, nullable=True)
    descricao_objeto = Column(Text, nullable=True)
    justificativa = Column(Text, nullable=True)

    valor_unitario = Column(String, nullable=True)   # mantém string para não quebrar por formato
    valor_total = Column(String, nullable=True)

    grau_prioridade = Column(String, nullable=True)
    data_pretendida = Column(String, nullable=True)

    municipios = Column(Text, nullable=True)
    riscos_nao_contratacao = Column(Text, nullable=True)

    renovacao_contrato = Column(String, nullable=True)
    modalidade_prevista = Column(String, nullable=True)
    duracao_total = Column(String, nullable=True)

    observacoes = Column(Text, nullable=True)

    # Guarda o restante das colunas do Excel (para detalhe) sem ficar criando 30 campos agora
    raw_json = Column(Text, nullable=True)

    imported_at = Column(DateTime, default=datetime.utcnow)

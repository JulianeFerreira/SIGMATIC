from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class BemPatrimonial(Base):
    __tablename__ = "bens_patrimoniais"

    id = Column(Integer, primary_key=True, autoincrement=True)

    tombamento = Column(String, unique=True, index=True, nullable=False)
    descricao = Column(Text, nullable=False)

    categoria = Column(String, nullable=True)
    marca = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    serial = Column(String, nullable=True)

    valor_aquisicao = Column(Numeric(14, 2), nullable=True)
    data_aquisicao = Column(Date, nullable=True)

    unidade_atual = Column(String, nullable=True)
    local_fisico = Column(String, nullable=True)

    responsavel_nome = Column(String, nullable=True)
    responsavel_matricula = Column(String, nullable=True)

    situacao = Column(String, nullable=False, default="em_uso")  # em_uso|ocioso|manutencao|baixado|extraviado
    observacoes = Column(Text, nullable=True)

    garantia_fim = Column(Date, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    movimentacoes = relationship("MovimentacaoPatrimonial", back_populates="bem", cascade="all, delete-orphan")

    def to_dict(self, include_history: bool = False):
        d = {
            "tombamento": self.tombamento,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "marca": self.marca,
            "modelo": self.modelo,
            "serial": self.serial,
            "valor_aquisicao": float(self.valor_aquisicao) if self.valor_aquisicao is not None else None,
            "data_aquisicao": self.data_aquisicao.isoformat() if self.data_aquisicao else None,
            "unidade_atual": self.unidade_atual,
            "local_fisico": self.local_fisico,
            "responsavel_nome": self.responsavel_nome,
            "responsavel_matricula": self.responsavel_matricula,
            "situacao": self.situacao,
            "observacoes": self.observacoes,
            "garantia_fim": self.garantia_fim.isoformat() if self.garantia_fim else None,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None,
            "atualizado_em": self.atualizado_em.isoformat() if self.atualizado_em else None,
        }
        if include_history:
            d["movimentacoes"] = [m.to_dict() for m in (self.movimentacoes or [])]
        return d

    @staticmethod
    def from_payload(p: dict) -> "BemPatrimonial":
        def as_date(v):
            if not v:
                return None
            if isinstance(v, date):
                return v
            return date.fromisoformat(v)

        return BemPatrimonial(
            tombamento=(p.get("tombamento") or "").strip(),
            descricao=(p.get("descricao") or "").strip(),
            categoria=p.get("categoria"),
            marca=p.get("marca"),
            modelo=p.get("modelo"),
            serial=p.get("serial"),
            valor_aquisicao=p.get("valor_aquisicao"),
            data_aquisicao=as_date(p.get("data_aquisicao")),
            unidade_atual=p.get("unidade_atual"),
            local_fisico=p.get("local_fisico"),
            responsavel_nome=p.get("responsavel_nome"),
            responsavel_matricula=p.get("responsavel_matricula"),
            situacao=p.get("situacao") or "em_uso",
            observacoes=p.get("observacoes"),
            garantia_fim=as_date(p.get("garantia_fim")),
        )


class MovimentacaoPatrimonial(Base):
    __tablename__ = "movimentacoes_patrimoniais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tombamento = Column(String, ForeignKey("bens_patrimoniais.tombamento"), index=True, nullable=False)

    tipo = Column(String, nullable=False)  # cadastro|transferencia|manutencao|baixa|emprestimo
    de_unidade = Column(String, nullable=True)
    para_unidade = Column(String, nullable=True)

    motivo = Column(Text, nullable=True)
    documento_ref = Column(String, nullable=True)

    usuario = Column(String, nullable=True)
    data = Column(DateTime, default=datetime.utcnow)

    bem = relationship("BemPatrimonial", back_populates="movimentacoes")

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "de_unidade": self.de_unidade,
            "para_unidade": self.para_unidade,
            "motivo": self.motivo,
            "documento_ref": self.documento_ref,
            "usuario": self.usuario,
            "data": self.data.isoformat() if self.data else None,
        }

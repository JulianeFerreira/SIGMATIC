from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models import ProcessoCompra  # <-- agora vem do models.py

BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_FILE = BASE_DIR / "GAA - Compras.xlsx"
SHEET_NAME = "Compras 2026"  # se quiser já deixar em 2026

def import_excel():
    Base.metadata.create_all(bind=engine)

    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

    # primeira linha é o cabeçalho real
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.dropna(how="all")

    db: Session = SessionLocal()

    for _, row in df.iterrows():
        processo = ProcessoCompra(
            numero_processo=row.get("PROCESSO N°"),
            descricao=row.get("DESCRIÇÃO"),
            data_criacao=row.get("DATA DE CRIAÇÃO"),
            valor_previsto=row.get("VALOR PREVISTO"),
            fonte_recurso=row.get("FONTE DE RECURSO"),
            modalidade=row.get("MODALIDADE"),
            data_pregao=row.get("DATA DO PREGÃO"),
            contrato_assinado=row.get("CONTRATO ASSINADO"),
            empenho_assinado=row.get("EMPENHO ASSINADO"),
            empenho_enviado_fornecedor=row.get("EMPENHO E CONTRATO ENVIADO AO FORNECEDOR (DATA)"),
            prazo_entrega_dias=row.get("PRAZO DE ENTREGA (DIAS)"),
            data_prev_entrega=row.get("DATA PREV. DE ENTREGA"),
            cobrado_entrega_dia=row.get("COBRADO ENTREGA NO DIA"),
            material_entregue_data=row.get("MATERIAL ENTREGUE (DATA)"),
            situacao=row.get("SITUAÇÃO"),
            observacao=row.get("OBSERVAÇÃO"),
        )
        db.add(processo)

    db.commit()
    db.close()
    print(f"Importação concluída! Linhas importadas: {len(df)}")


if __name__ == "__main__":
    import_excel()

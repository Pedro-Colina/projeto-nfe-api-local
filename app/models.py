from sqlalchemy import Column, Integer, String, Float, Text
from app.config import Base

class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    arquivo = Column(Text)
    documento = Column(String(20))
    cliente = Column(Text)
    transportadora = Column(Text)
    mensagem = Column(Text)
    data_emissao = Column(String(50))
    chave_acesso = Column(String(60), unique=True, index=True)
    numero_nota = Column(String(20))
    valor = Column(Float)
    cnpj_emitente = Column(String(20))
    nome_emitente = Column(Text)

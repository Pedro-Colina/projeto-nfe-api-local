from pydantic import BaseModel
from datetime import datetime

class NotaSchema(BaseModel):
    arquivo: str
    documento: str
    cliente: str
    transportadora: str | None = None
    mensagem: str | None = None
    data_emissao: datetime
    chave_acesso: str
    numero_nota: str
    valor: float
    cnpj_emitente: str
    nome_emitente: str

    class Config:
        orm_mode = True

from app.config import engine, SessionLocal, Base
from app.models import Nota
from sqlalchemy.exc import IntegrityError

def criar_tabela():
    """Cria as tabelas no banco se não existirem."""
    Base.metadata.create_all(bind=engine)

def inserir_varias_notas(notas: list[dict]):
    """Insere várias notas no banco."""
    session = SessionLocal()
    try:
        objs = [Nota(**nota) for nota in notas]
        session.add_all(objs)
        session.commit()
    except IntegrityError:
        session.rollback()
    finally:
        session.close()

def busca_duplicidade():
    """Retorna todas as chaves de acesso já salvas."""
    session = SessionLocal()
    try:
        chaves = session.query(Nota.chave_acesso).all()
        return [row[0] for row in chaves]
    finally:
        session.close()

def buscar_nota_mais_recente(documento: str):
    """Busca a nota mais recente de um documento."""
    session = SessionLocal()
    try:
        nota = (
            session.query(Nota)
            .filter(Nota.documento == documento)
            .order_by(Nota.data_emissao.desc())
            .first()
        )
        if nota:
            return {
                "arquivo": nota.arquivo,
                "documento": nota.documento,
                "cliente": nota.cliente,
                "transportadora": nota.transportadora,
                "mensagem": nota.mensagem,
                "data_emissao": nota.data_emissao,
                "chave_acesso": nota.chave_acesso,
                "numero_nota": nota.numero_nota,
                "valor": nota.valor,
                "cnpj_emitente": nota.cnpj_emitente,
                "nome_emitente": nota.nome_emitente,
            }
        return None
    finally:
        session.close()

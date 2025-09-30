from app.config import engine, async_session, Base
from app.models import Nota
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
import asyncio

async def criar_tabela():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def inserir_varias_notas(notas: list[dict]):
    async with async_session() as session:
        objs = [Nota(**nota) for nota in notas]
        session.add_all(objs)
        try:
            await session.commit()
        except IntegrityError:  # chave_acesso duplicada
            await session.rollback()

async def busca_duplicidade():
    async with async_session() as session:
        result = await session.execute(select(Nota.chave_acesso))
        return [row[0] for row in result.all()]

async def buscar_nota_mais_recente(documento: str):
    async with async_session() as session:
        result = await session.execute(
            select(Nota)
            .where(Nota.documento == documento)
            .order_by(Nota.data_emissao.desc())
            .limit(1)
        )
        row = result.scalars().first()
        if row:
            return {
                "arquivo": row.arquivo,
                "documento": row.documento,
                "cliente": row.cliente,
                "transportadora": row.transportadora,
                "mensagem": row.mensagem,
                "data_emissao": row.data_emissao,
                "chave_acesso": row.chave_acesso,
                "numero_nota": row.numero_nota,
                "valor": row.valor,
                "cnpj_emitente": row.cnpj_emitente,
                "nome_emitente": row.nome_emitente,
            }
    return None

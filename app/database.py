# app/database.py
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "notas.db"
DB_URL = str(DB_PATH)

async def criar_tabela():
    async with aiosqlite.connect(DB_URL, timeout=30) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arquivo TEXT,
                documento TEXT,
                cliente TEXT,
                transportadora TEXT,
                mensagem TEXT,
                data_emissao TEXT,
                chave_acesso TEXT UNIQUE
            )
        """)
        await db.commit()

async def inserir_varias_notas(notas: list[dict]):
    if not notas:
        return
    async with aiosqlite.connect(DB_URL, timeout=30) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA synchronous=NORMAL;")
        sql = """
            INSERT OR IGNORE INTO notas
            (arquivo, documento, cliente, transportadora, mensagem, data_emissao, chave_acesso)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        data = [
            (
                nota["arquivo"],
                nota["documento"],
                nota["cliente"],
                nota["transportadora"],
                nota["mensagem"],
                nota["data_emissao"],
                nota["chave_acesso"]
            )
            for nota in notas
        ]
        await db.executemany(sql, data)
        await db.commit()

async def busca_duplicidade():
    async with aiosqlite.connect(DB_URL, timeout=5) as db:
        cur = await db.execute("SELECT chave_acesso FROM notas")
        rows = await cur.fetchall()
        await cur.close()
        return [r[0] for r in rows]

async def buscar_nota_mais_recente(documento: str):
    async with aiosqlite.connect(DB_URL, timeout=5) as db:
        cur = await db.execute("""
            SELECT arquivo, documento, cliente, transportadora, mensagem, data_emissao, chave_acesso
            FROM notas
            WHERE documento = ?
            ORDER BY datetime(data_emissao) DESC
            LIMIT 1
        """, (documento,))
        row = await cur.fetchone()
        await cur.close()
        if row:
            return {
                "arquivo": row[0],
                "documento": row[1],
                "cliente": row[2],
                "transportadora": row[3],
                "mensagem": row[4],
                "data_emissao": row[5],
                "chave_acesso": row[6],
            }
    return None

# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
import aiofiles
import traceback
from contextlib import asynccontextmanager

from app.utils import upload_lote
from app.database import buscar_nota_mais_recente, criar_tabela

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # cria a tabela antes de aceitar requisições
        await criar_tabela()
        print("DB: tabela verificada/criada com sucesso.")
        yield
    except Exception:
        print("Erro ao inicializar o DB:")
        traceback.print_exc()
        raise

app = FastAPI(
    title="API de Consulta de NF-e",
    description="Consulta a NF-e mais recente com base no CPF ou CNPJ do cliente",
    version="1.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="views"), name="static")


@app.get("/", include_in_schema=False)
async def home():
    async with aiofiles.open("views/index.html", mode="r") as f:
        content = await f.read()
    return HTMLResponse(content=content)

@app.get("/consulta", tags=["Consultas"])
async def consulta_por_documento(documento: str):
    resultado = await buscar_nota_mais_recente(documento)
    if resultado:
        return resultado
    raise HTTPException(status_code=404, detail="Nota não encontrada para o documento informado.")

@app.post("/notas/upload-lote", tags=["Importar XMLs"])
async def upload_lote_post(files: List[UploadFile] = File(...)):
    resultado = await upload_lote(files)
    if resultado:
        return resultado
    return {"message": "Nenhuma nota importada para o sistema..."}

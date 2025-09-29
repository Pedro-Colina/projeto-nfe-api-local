# app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
import aiofiles

from app.utils import upload_lote
from app.config import XML_FOLDER
from app.database import buscar_nota_mais_recente, criar_tabela


app = FastAPI(
    title="API de Consulta de NF-e",
    description="Consulta a NF-e mais recente com base no CPF ou CNPJ do cliente",
    version="1.0"
)

async def lifespan():
    # executa ao iniciar
    await criar_tabela()
    yield

app.mount("/static", StaticFiles(directory="views"), name="static")


@app.get("/", include_in_schema=False)
async def home():
    async with aiofiles.open("views/index.html", mode="r") as f:
        content = await f.read()
    return HTMLResponse(content=content)

@app.get("/consulta/{documento}", tags=["Consultas"])
async def consulta_por_documento(documento: str):
    resultado = await buscar_nota_mais_recente(documento)
    if resultado:
        return resultado
    return {"message": "Nenhuma nota encontrada para esse CPF/CNPJ"}

@app.post("/notas/upload-lote", tags=["Importar XMLs"])
async def upload_lote_post(files: List[UploadFile] = File(...)):
    resultado = await upload_lote(files)
    if resultado:
        return resultado
    return {"message": "Nenhuma nota importada para o sistema..."}

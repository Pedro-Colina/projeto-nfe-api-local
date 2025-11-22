import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
import aiofiles
from app.config import Base, engine
from app.utils import upload_lote
from app.database import buscar_nota_mais_recente
from app.schemas import NotaSchema
from typing import List

app = FastAPI(
    title="API de Consulta de NF-e",
    description="Consulta a NF-e mais recente com base no CPF ou CNPJ do cliente",
    version="1.0"
)

# Cria tabela ao iniciar
@app.get("/init-db")
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        return {"message": "Tabelas criadas com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/static", StaticFiles(directory="views"), name="static")

@app.get("/", include_in_schema=False)
async def home():
    async with aiofiles.open("views/index.html", mode="r") as f:
        content = await f.read()
    return HTMLResponse(content=content)

@app.get("/consulta", response_model=List[NotaSchema],tags=["Consultas"])
async def consulta_por_documento(documento: str):
    resultado = await asyncio.to_thread(buscar_nota_mais_recente, documento)
    if resultado:
        return resultado
    raise HTTPException(status_code=404, detail="Nota não encontrada para o documento informado.")

@app.post("/notas/upload-lote", tags=["Importar XMLs"])
async def upload_lote_post(files: List[UploadFile] = File(...)):
    return await upload_lote(files)

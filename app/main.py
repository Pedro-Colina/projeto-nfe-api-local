from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from .utils import buscar_nota_mais_recente_por_documento
import os
from app.utils import processa_xml
from app.config import XML_FOLDER
from app.database import buscar_nota_mais_recente, criar_tabela, inserir_nota
import importar_xmls
import sqlite3

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from typing import List
import tempfile, os, aiofiles, traceback

app = FastAPI(
    title="API de Consulta de NF-e",
    description="Consulta a NF-e mais recente com base no CPF ou CNPJ do cliente",
    version="1.0"
    docs_url=None,       # Desabilita Swagger
    redoc_url="/docs",   # Coloca Redoc no lugar do /docs
)

def importar_xml():
    criar_tabela()  # garante que a tabela existe

    arquivos_processados = 0
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            filepath = os.path.join(XML_FOLDER, filename)

            # Aqui não passamos documento alvo, então forçamos processamento de todos
            nota = processa_xml(filepath, filename, documento_target=None)

            if nota:
                arquivos_processados += 1

    print(f"Importação concluída! {arquivos_processados} arquivos processados.")

if __name__ == "__main__":
    importar_xml()


@app.get("/consulta/{documento}", tags=["Consultas"])
def consulta_por_documento(documento: str):
    resultado = buscar_nota_mais_recente(documento)
    if resultado:
        return resultado
    return {"message": "Nenhuma nota encontrada para esse CPF/CNPJ"}

# @app.post("/importar", tags=["Importar XML"])
# def importar_notas():
#     """
#     Importa os XMLs da pasta para o banco de dados.
#     """
#     msg = importar_xmls.importar_xmls()
#     return {"mensagem": msg}

def dividir_em_lotes(lista, tamanho_lote):
    """Divide uma lista em blocos de tamanho fixo"""
    for i in range(0, len(lista), tamanho_lote):
        yield lista[i:i + tamanho_lote]


@app.post("/notas/upload-lote", tags=["Importar XMLs"])
async def upload_lote(files: List[UploadFile] = File(...)):
    """
    Recebe XMLs em massa, divide em blocos menores e insere no SQLite.
    Ignora duplicados (chave_acesso).
    """
    BATCH_SIZE = 200
    notas_inseridas, erros, duplicados = [], [], []

    for batch in dividir_em_lotes(files, BATCH_SIZE):
        for file in batch:
            try:
                # salva temporário
                tmp_fd, tmp_path = tempfile.mkstemp(suffix=".xml")
                os.close(tmp_fd)
                contents = await file.read()
                async with aiofiles.open(tmp_path, 'wb') as tmp:
                    await tmp.write(contents)

                nota_dict = processa_xml(tmp_path, file.filename)
                os.remove(tmp_path)

                if not nota_dict:
                    erros.append({"arquivo": file.filename, "erro": "XML inválido"})
                    continue

                # verifica duplicados pela chave_acesso
                conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "notas.db"))
                cur = conn.cursor()
                cur.execute("SELECT id FROM notas WHERE chave_acesso = ?", (nota_dict["chave_acesso"],))
                existe = cur.fetchone()
                conn.close()

                if existe:
                    duplicados.append(nota_dict["chave_acesso"])
                    continue

                inserir_nota(nota_dict)
                notas_inseridas.append(nota_dict)

            except Exception as e:
                erros.append({"arquivo": file.filename, "erro": str(e)})

    return {
        "sucesso": len(notas_inseridas),
        "duplicados": len(duplicados),
        "falhas": len(erros),
        "notas_inseridas": notas_inseridas[:5],  # exibe só os primeiros 5 para não sobrecarregar
        "erros": erros
    }

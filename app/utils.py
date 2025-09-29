# app/utils.py
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from typing import Optional, List
from .config import XML_FOLDER
from .mensagens import get_mensagem
from app.database import inserir_varias_notas, busca_duplicidade
from fastapi import UploadFile, File
from dotenv import load_dotenv
load_dotenv()
import asyncio
import aiofiles
import tempfile

noinf = "Não informado"

def local_name(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag

def find_tag(root: ET.Element, path: str) -> Optional[ET.Element]:
    parts = path.split("/")
    current = root
    for part in parts:
        found = None
        for el in current.iter():
            if local_name(el.tag) == part:
                found = el
                break
        if found is None:
            return None
        current = found
    return current

def get_access_key(root: ET.Element) -> Optional[str]:
    infnfe = find_tag(root, "infNFe")
    if infnfe is not None:
        chave = infnfe.attrib.get("Id", "")
        if chave.startswith("NFe"):
            chave = chave[3:]
        return chave if chave else None
    return noinf

def get_client_document(root: ET.Element) -> Optional[str]:
    cpf_tag = find_tag(root, "dest/CPF")
    cnpj_tag = find_tag(root, "dest/CNPJ")
    if cpf_tag is not None:
        return cpf_tag.text
    if cnpj_tag is not None:
        return cnpj_tag.text
    return None

def get_emission_date(root: ET.Element) -> Optional[str]:
    data_tag = find_tag(root, "ide/dhEmi")
    if data_tag is not None and data_tag.text:
        try:
            return datetime.fromisoformat(data_tag.text).isoformat()
        except Exception:
            return data_tag.text[:10]
    return None

def text_in_tag(tag: str, root) -> str:
    found_tag = find_tag(root, tag)
    return found_tag.text if found_tag is not None else noinf

# processa_xml continua para uso local (arquivo no disco)
def processa_xml(filepath: str, filename: str, documento_target: Optional[str] = None):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        doc_cliente = get_client_document(root)
        if documento_target and doc_cliente != documento_target:
            return None

        nome_cliente = text_in_tag("dest/xNome", root)
        transportadora = text_in_tag("transp/transporta/xNome", root)
        n_nf = text_in_tag("ide/nNF", root)
        cnpj = text_in_tag("emit/CNPJ", root)
        chave_acess = get_access_key(root)
        data_emissao = get_emission_date(root)
        mensagem = get_mensagem(transportadora, n_nf, doc_cliente, cnpj)

        nota = {
            "arquivo": filename,
            "documento": doc_cliente or noinf,
            "cliente": nome_cliente,
            "transportadora": transportadora,
            "mensagem": mensagem,
            "data_emissao": data_emissao or noinf,
            "chave_acesso": chave_acess
        }

        return nota
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
        return None

def dividir_em_lotes(lista, tamanho_lote):
    for i in range(0, len(lista), tamanho_lote):
        yield lista[i:i + tamanho_lote]

# --- helper: parse XML a partir de bytes (para evitar escrever temp file se preferir) ---
def parse_xml_from_bytes(contents: bytes, filename: str):
    try:
        root = ET.fromstring(contents)
        # reusar lógica do processa_xml a partir do root
        doc_cliente = get_client_document(root)
        nome_cliente = text_in_tag("dest/xNome", root)
        transportadora = text_in_tag("transp/transporta/xNome", root)
        valor_nf = text_in_tag("total/ICMSTot/vNF", root)
        n_nf = text_in_tag("ide/nNF", root)
        cnpj = text_in_tag("emit/CNPJ", root)
        nome_empresa = text_in_tag("emit/xNome", root)
        chave_acess = get_access_key(root)
        data_emissao = get_emission_date(root)
        mensagem = get_mensagem(transportadora, n_nf, doc_cliente, cnpj)

        nota = {
            "arquivo": filename,
            "documento": doc_cliente or noinf,
            "cliente": nome_cliente,
            "transportadora": transportadora,
            "mensagem": mensagem,
            "data_emissao": data_emissao or noinf,
            "chave_acesso": chave_acess,
            "numero_nota": n_nf or noinf,
            "valor": float(valor_nf) if valor_nf.replace('.', '', 1).isdigit() else 0.0,
            "cnpj_emitente": cnpj or noinf,
            "nome_emitente": nome_empresa or noinf
        }
        return nota
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
        # retorna None em caso de erro
        return None

async def process_file(file: UploadFile, salvos_set: set, erros: list, duplicados: list, notas_inserir: list):
    try:
        contents = await file.read()

        # limita concorrência de parsing
        nota_dict = await asyncio.to_thread(parse_xml_from_bytes, contents, file.filename)

        if not isinstance(nota_dict, dict):
            erros.append({"arquivo": file.filename, "erro": "XML inválido"})
            return

        chave = nota_dict.get("chave_acesso")
        if not chave:
            erros.append({"arquivo": file.filename, "erro": "Sem chave de acesso"})
            return

        if chave in salvos_set:
            duplicados.append(chave)
            return

        notas_inserir.append(nota_dict)
        salvos_set.add(chave)

    except Exception as e:
        erros.append({"arquivo": file.filename if hasattr(file, "filename") else "unknown", "erro": str(e), "local": "process_file"})

async def upload_lote(files: List[UploadFile] = File(...)):
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))  # default 100
    erros, duplicados, notas_sucesso = [], [], []

    salvos = await busca_duplicidade()
    salvos_set = set(salvos)

    for batch in dividir_em_lotes(files, BATCH_SIZE):
        # processa todos os arquivos do lote em paralelo
        notas_inserir = []
        tasks = [process_file(file, salvos_set, erros, duplicados, notas_inserir) for file in batch]
        await asyncio.gather(*tasks)

        if notas_inserir:
            try:
                await inserir_varias_notas(notas_inserir)  # agora async
                notas_sucesso.extend(notas_inserir)
            except Exception as e:
                erros.append({"arquivo": "lote", "erro": str(e), "local": "db insert"})

    return {
        "sucesso": len(notas_sucesso),
        "duplicados": len(duplicados),
        "falhas": len(erros),
        "notas_inserir": notas_sucesso[:5],
        "erros": erros
    }

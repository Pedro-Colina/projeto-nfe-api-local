import xml.etree.ElementTree as ET
import os
from datetime import datetime
from typing import Optional, List
from .mensagens import get_mensagem
from app.database import inserir_varias_notas, busca_duplicidade
from fastapi import UploadFile, File
from dotenv import load_dotenv
import asyncio

load_dotenv()

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

def parse_xml_from_bytes(contents: bytes, filename: str):
    try:
        root = ET.fromstring(contents)
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

        return {
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
    except Exception as e:
        print(f"Erro ao processar {filename}: {e}")
        return None

async def process_file(file: UploadFile, salvos_set: set, erros: list, duplicados: list, notas_inserir: list):
    try:
        contents = await file.read()
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
        erros.append({"arquivo": getattr(file, "filename", "unknown"), "erro": str(e)})

async def upload_lote(files: List[UploadFile] = File(...)):
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))
    erros, duplicados, notas_sucesso = [], [], []

    # 🔽 Agora busca_duplicidade é síncrono
    salvos = await asyncio.to_thread(busca_duplicidade)
    salvos_set = set(salvos)

    for batch_start in range(0, len(files), BATCH_SIZE):
        batch = files[batch_start:batch_start + BATCH_SIZE]
        notas_inserir = []
        tasks = [process_file(file, salvos_set, erros, duplicados, notas_inserir) for file in batch]
        await asyncio.gather(*tasks)

        if notas_inserir:
            # 🔽 Inserção também síncrona
            await asyncio.to_thread(inserir_varias_notas, notas_inserir)
            notas_sucesso.extend(notas_inserir)

    return {
        "sucesso": len(notas_sucesso),
        "duplicados": len(duplicados),
        "falhas": len(erros),
        "notas_inserir": notas_sucesso[:5],
        "erros": erros
    }

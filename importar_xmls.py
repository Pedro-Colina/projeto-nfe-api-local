import os
import shutil
import requests

# URL da sua API no Render
API_URL = "https://projeto-nfe-api-local.onrender.com/notas/upload-lote"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta do script (/projeto)
ROOT_DIR = os.path.dirname(BASE_DIR)  # sobe 1 nível (/projeto-nfe-api)

XML_FOLDER = os.path.join(ROOT_DIR, "xmls")
PROCESSED_FOLDER = os.path.join(ROOT_DIR, "processados")


def enviar_xmls():
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    xml_files = []
    filepaths = []

    # Junta todos os arquivos XML em uma lista
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            filepath = os.path.join(XML_FOLDER, filename)
            filepaths.append((filepath, filename))

            with open(filepath, "rb") as f:
                xml_files.append(("files", (filename, f.read(), "application/xml")))

    if not xml_files:
        print("⚠️ Nenhum XML encontrado na pasta.")
        return

    try:
        # Envia todos os arquivos em lote
        response = requests.post(API_URL, files=xml_files)

        if response.status_code == 200:
            print(f"✅ {len(xml_files)} XML(s) enviados com sucesso!")
            # Move arquivos para pasta de processados
            for filepath, filename in filepaths:
                shutil.move(filepath, os.path.join(PROCESSED_FOLDER, filename))
        else:
            print(f"❌ Erro ao enviar XMLs: {response.status_code} -> {response.text}")

    except Exception as e:
        print(f"⚠️ Erro ao enviar XMLs: {e}")


if __name__ == "__main__":
    enviar_xmls()

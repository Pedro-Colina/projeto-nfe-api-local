import os
import shutil
import requests

# URL da sua API no Render
API_URL = "https://projeto-nfe-api-local.onrender.com/notas/upload-lote"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # pasta do script (/projeto)
ROOT_DIR = os.path.dirname(BASE_DIR)  # sobe 1 nível (/projeto-nfe-api)

XML_FOLDER = os.path.join(ROOT_DIR, "xmls")
PROCESSED_FOLDER = os.path.join(ROOT_DIR, "processados")

# Pasta onde serão movidos os XMLs já enviados
PROCESSED_FOLDER = "./processados"

def enviar_xmls():
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)

    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            filepath = os.path.join(XML_FOLDER, filename)
            processed_path = os.path.join(PROCESSED_FOLDER, filename)

            try:
                with open(filepath, "rb") as f:
                    file_content = f.read()  # lê em memória

                files = {"file": (filename, file_content, "application/xml")}
                response = requests.post(API_URL, files=files)

                if response.status_code == 200:
                    print(f"✅ {filename} enviado com sucesso!")
                    shutil.move(filepath, processed_path)  # só move depois de fechar
                else:
                    print(f"❌ Erro ao enviar {filename}: {response.text}")

            except Exception as e:
                print(f"⚠️ Erro ao processar {filename}: {e}")

if __name__ == "__main__":
    enviar_xmls()

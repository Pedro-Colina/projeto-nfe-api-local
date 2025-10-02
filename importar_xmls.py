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
    if not os.path.exists(PROCESSED_FOLDER):
        os.makedirs(PROCESSED_FOLDER)

    files = []
    xml_paths = []
    
    for filename in os.listdir(XML_FOLDER):
        if filename.endswith(".xml"):
            filepath = os.path.join(XML_FOLDER, filename)
            xml_paths.append(filepath)
            files.append(('files', (filename, open(filepath, 'rb'), 'application/xml')))
    
    if not files:
        print("Nenhum XML encontrado para envio.")
        return
    
    try:
        response = requests.post(API_URL, files=files)
        if response.status_code == 200:
            print("✅ XMLs enviados com sucesso:", response.json())
            # Mover os arquivos para a pasta processados
            for filepath in xml_paths:
                dest_path = os.path.join(PROCESSED_FOLDER, os.path.basename(filepath))
                shutil.move(filepath, dest_path)
            print(f"✅ {len(xml_paths)} arquivos movidos para {PROCESSED_FOLDER}")
        else:
            print("❌ Erro ao enviar:", response.status_code, response.text)
    except Exception as e:
        print("❌ Erro de conexão:", e)

if __name__ == "__main__":
    enviar_xmls()

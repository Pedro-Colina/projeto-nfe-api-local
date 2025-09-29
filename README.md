# 📦 API de Processamento de Notas Fiscais (XML)

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

API desenvolvida em **FastAPI** com **SQLite (aiosqlite)** para processar, armazenar e consultar **Notas Fiscais Eletrônicas (NFe)** no formato **XML**.  
Inclui um **front-end simples em HTML/CSS/JS** para upload dos arquivos.

---

## 🚀 Funcionalidades

- 📂 Upload de múltiplos arquivos XML (input ou drag-and-drop).
- ✅ Validação e tratamento de arquivos inválidos.
- 🗄️ Inserção no banco com **controle de duplicidade** (`chave_acesso`).
- 💾 Armazenamento dos seguintes dados no banco:
  - `arquivo`
  - `documento`
  - `cliente`
  - `transportadora`
  - `mensagem`
  - `data_emissao`
  - `chave_acesso` (único)
  - `numero_nota`
  - `valor`
  - `cnpj_emitente`
  - `emitente`
- 🔎 Consulta da nota **mais recente** por documento.
- 🌐 Interface web em `/static/index.html`.

---

## 📂 Estrutura do Projeto

```
.
├── app/
│   ├── main.py          # Ponto de entrada FastAPI
│   ├── database.py      # Conexão e funções do banco
│   ├── utils.py         # Funções auxiliares de parse XML
│   └── views/           # Front-end (HTML, CSS, JS)
│       ├── index.html
│       ├── style.css
│       └── index.js
├── notas.db             # Banco SQLite (gerado automaticamente)
├── requirements.txt     # Dependências do projeto
└── README.md
```

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Inicialize o banco

```bash
python -m app.database
```

---

## ▶️ Executando o servidor

```bash
uvicorn app.main:app --reload
```

O servidor ficará disponível em:

- 🌐 API Base: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- 📑 Documentação Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- 📘 Documentação ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- 🖥️ Front-end: [http://127.0.0.1:8000/static/index.html](http://127.0.0.1:8000/static/index.html)

---

## 📑 Endpoints Principais

### 🔼 `POST /upload`

Upload de múltiplos arquivos XML.

**Resposta de exemplo:**

```json
{
  "sucesso": 5,
  "duplicados": 2,
  "falhas": 1,
  "notas_inserir": ["123.xml", "456.xml"],
  "erros": [
    {
      "arquivo": "lote1.xml",
      "erro": "XML inválido",
      "local": "parser"
    }
  ]
}
```

---

### 🔍 `GET /consulta/{documento}`

Consulta a nota **mais recente** de um documento.

**Exemplo de resposta:**

```json
{
  "arquivo": "123.xml",
  "documento": "12345678000199",
  "cliente": "Cliente Exemplo",
  "transportadora": "Transportadora ABC",
  "mensagem": "Pedido entregue",
  "data_emissao": "2025-09-29T10:00:00",
  "chave_acesso": "12345678901234567890123456789012345678901234",
  "numero_nota": "4567",
  "valor": 1500.75,
  "cnpj_emitente": "11222333000144",
  "emitente": "Empresa Emitente LTDA"
}
```

---

## 📌 Observações Importantes

- O banco utiliza **WAL mode** para reduzir bloqueios de concorrência.
- Se aparecer `database is locked`, reduza o `timeout` da conexão (ex.: `5s`).
- Para volumes muito grandes, considere migrar para **PostgreSQL** ou **MySQL**.

---

## 🖼️ Screenshots

<img width="1880" height="938" alt="image" src="https://github.com/user-attachments/assets/0980fe25-4fcf-4130-948b-e2c5e70ba30e" />


---

## 📜 Licença

Distribuído sob a licença MIT.  
Sinta-se livre para usar, modificar e distribuir.

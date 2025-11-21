const fileInput = document.getElementById("file-input");
const loading = document.getElementById("loading");
const fileList = document.getElementById("file-list");
const invalidArchive = document.getElementById("invalid-archiv");
const selectFilesButton = document.getElementById("select-files");
const contArchivesHtml = document.getElementById("contador-arquivos");
const dropZone = document.getElementById("drop-zone");
const selectedFiles = [];
const arquivosInvalidos = [];

selectFilesButton.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", () => {
  for (let file of fileInput.files) {
    if (file.type !== "text/xml" && file.type !== "application/xml") {
      arquivosInvalidos.push(file.name);
      continue;
    }
    selectedFiles.push(file);
  }
  renderInvalidFiles();
  renderFileList();
});

function renderInvalidFiles() {
  invalidArchive.innerHTML = "";
  const div = document.createElement("div");
  div.id = "invalid-files-message";
  if (arquivosInvalidos.length !== 0) {
    const p = document.createElement("strong");
    const validos = document.createElement("p");
    p.textContent = `Você selecionou ${arquivosInvalidos.length} arquivo(s) inválido(s). Apenas arquivos XML são permitidos.`;
    if (selectedFiles.length > 0) {
      validos.textContent = `Os ${selectedFiles.length} arquivos válidos foram mantidos.`;
    }
    const okButton = document.createElement("button");
    okButton.textContent = "OK";
    okButton.style.marginLeft = "10px";
    okButton.onclick = () => {
      arquivosInvalidos.length = 0;
      invalidArchive.innerHTML = "";
      invalidArchive.style.padding = "0px";
    };
    div.appendChild(p);
    div.appendChild(validos);
    invalidArchive.appendChild(div);
    invalidArchive.appendChild(okButton);
    invalidArchive.style.padding = "8px";
  }
}

function renderFileList() {
  fileList.innerHTML = "";
  for (const [index, file] of selectedFiles.entries()) {
    const li = document.createElement("li");
    li.textContent = file.name + " ";
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "X";
    removeBtn.style.marginLeft = "10px";
    removeBtn.onclick = () => {
      selectedFiles.splice(index, 1);
      renderFileList();
    };
    li.appendChild(removeBtn);
    fileList.appendChild(li);
  }
  contArchivesHtml.innerText = "";
  if (selectedFiles.length > 0) {
    contArchivesHtml.innerHTML = `Total de arquivos selecionados: <strong>${selectedFiles.length}</strong>`;
  }
}

function formataDocumentoViews(doc) {
  const docLimpo = String(doc).replaceAll(/\D/g, "");
  if (docLimpo.length === 11) {
    return docLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
  } else if (docLimpo.length === 14) {
    return docLimpo.replace(
      /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
      "$1.$2.$3/$4-$5"
    );
  }

  return doc;
}

function formataDocumentoApp(doc) {
  const docLimpo = String(doc).replaceAll(/\D/g, "");
  if (docLimpo.length === 11) {
    return docLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1$2$3$4");
  } else if (docLimpo.length === 14) {
    return docLimpo.replace(
      /(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,
      "$1$2$3$4$5"
    );
  }

  return doc;
}

function adicionaAccordeon() {
  const accordions = document.getElementsByClassName("accordion");
  for (const accordion of accordions) {
    accordion.addEventListener("click", function () {
      this.classList.toggle("active");
      this.getElementsByClassName("icon")[0].classList.toggle("active");
      const panel = this.nextElementSibling;
      panel.classList.toggle("display-none");
    });
  }
}

function renderArquivosEnviados(arquivos) {
  let html = "";
  html += `<h2>Resultado do Upload</h2>`;
  html += `<p>Total de notas cadastradas: <strong>${arquivos.sucesso}</strong></p>`;
  html += `<p>Total de arquivos duplicados: <strong>${arquivos.duplicados}</strong></p>`;
  html += `<p>Total de arquivos com erro: <strong>${arquivos.falhas}</strong></p>`;

  if (arquivos.erros && arquivos.erros.length > 0) {
    html += `<button class="accordion">Detalhes dos erros: <span class="icon" aria-hidden="true"></span></button>`;
    html += `<div class="panel display-none">`;
    html += `<ul>`;
    for (let erro of arquivos.erros) {
      html += `<li><strong>${erro.arquivo}:</strong> ${erro.erro}</li>`;
    }
    html += `</ul>`;
    html += `</div>`;
  }

  if (arquivos.notas_inserir.length > 0) {
    html += `<button class="accordion" aria-expanded="false">Amostra notas inseridas( ${arquivos.notas_inserir.length} ultimas )<span class="icon" aria-hidden="true"></span></button>`;
    html += `<div class="panel display-none">`;
    html += `<pre>${JSON.stringify(arquivos.notas_inserir, null, 2)}</pre>`;
    html += `</div>`;
  }
  return html;
}

function renderArquivoEncontrado(arquivo) {
  let html = "";

  if (arquivo.chave_acesso === undefined) {
    html = "<p>Nenhuma nota encontrada para este documento.</p>";
    document.getElementById("consulta-response").innerHTML = html;
    return;
  }

  let data_emissao = new Date(arquivo.data_emissao).toLocaleString("pt-BR", {
    timeZone: "America/Sao_Paulo",
    day: "numeric",
    month: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  let mascara_doc = formataDocumentoViews(arquivo.documento);
  let mascara_doc_emit = formataDocumentoViews(arquivo.cnpj_emitente);
  let valor = Number.isInteger(arquivo.valor)
    ? arquivo.valor.toLocaleString("pt-BR", {
        currency: "BRL",
        style: "currency",
      })
    : "Valor não definido";

  html =
    "<h1>Nota Fiscal</h1>" +
    "<p><strong>Chave de Acesso: </strong> " +
    arquivo.chave_acesso +
    "</p>" +
    "<p><strong>Numero da NF: </strong> " +
    arquivo.numero_nota +
    "</p>" +
    "<p><strong>Empresa emitente: </strong> " +
    arquivo.nome_emitente +
    "</p>" +
    "<p><strong>CNPJ emitente: </strong> " +
    mascara_doc_emit +
    "</p>" +
    "<p><strong>Destinatário: </strong> " +
    arquivo.cliente +
    "</p>" +
    "<p><strong>Documento cliente: </strong> " +
    mascara_doc +
    "</p>" +
    "<p><strong>Data de Emissão: </strong> " +
    data_emissao +
    "</p>" +
    "<p><strong>Transportadora: </strong> " +
    arquivo.transportadora +
    "</p>" +
    "<p><strong>Valor NF: </strong> " +
    valor +
    "</p>" +
    "<p><strong>Mensagem: </strong> " +
    arquivo.mensagem +
    "</p>";

  return html;
}

function mostraHTML(objetoHTML) {
  objetoHTML.classList.remove("display-none");
}

function escondeHTML(objetoHTML) {
  objetoHTML.classList.add("display-none");
}

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");

  const files = event.dataTransfer.files;
  for (let file of files) {
    if (file.type !== "text/xml" && file.type !== "application/xml") {
      arquivosInvalidos.push(file.name);
      continue;
    }
    selectedFiles.push(file);
  }
  renderInvalidFiles();
  renderFileList();
});

document
  .getElementById("upload-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    mostraHTML(loading);
    const formData = new FormData();

    for (const file of selectedFiles) {
      formData.append("files", file);
    }

    try {
      const response = await fetch("/notas/upload-lote", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      escondeHTML(loading);
      document.getElementById("response").innerHTML =
        renderArquivosEnviados(result);
      adicionaAccordeon();
    } catch (error) {
      escondeHTML(loading);
      document.getElementById("response").innerText =
        "Erro ao enviar: " + error.message;
    }
  });

document
  .getElementById("consulta-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    mostraHTML(loading);
    const documento = formataDocumentoApp(event.target.documento.value);
    try {
      const response = await fetch(`/consulta?documento=${documento}`);
      console.log("response", response);
      if (!response.ok) {
        throw new Error("Nota não encontrada");
      }
      const nota = await response.json();
      escondeHTML(loading);
      document.getElementById("consulta-response").innerHTML =
        renderArquivoEncontrado(nota);
    } catch (error) {
      escondeHTML(loading);
      document.getElementById("consulta-response").innerText =
        "Erro: " + error.message;
    }
  });

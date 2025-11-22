const fileInput = document.getElementById("file-input");
const loading = document.getElementById("loading");
const fileList = document.getElementById("file-list");
const invalidArchive = document.getElementById("invalid-archiv");
const selectFilesButton = document.getElementById("select-files");
const cleanUploadButton = document.getElementById("clean-upload");
const contArchivesHtml = document.getElementById("contador-arquivos");
const contadorArquivosDiv = document.getElementById("file-cont");
const dropZone = document.getElementById("drop-zone");
const selectedFiles = [];
const arquivosInvalidos = [];

function getSelectedFiles() {
  return selectedFiles;
}

function renderArquivosEnviados(arquivos) {
  let html = "";
  html += `<h2>Resultado do Upload</h2>`;
  html += `<p>Total de notas cadastradas: <strong>${arquivos.sucesso}</strong></p>`;
  html += `<p>Total de arquivos duplicados: <strong>${arquivos.duplicados}</strong></p>`;
  html += `<p>Total de arquivos com erro: <strong>${arquivos.falhas}</strong></p>`;

  if (arquivos.erros && arquivos.erros.length > 0) {
    html += `<button class="accordion upload">Detalhes dos erros: <span class="icon" aria-hidden="true"></span></button>`;
    html += `<div class="panel display-none">`;
    html += `<ul>`;
    for (let erro of arquivos.erros) {
      html += `<li><strong>${erro.arquivo}:</strong> ${erro.erro}</li>`;
    }
    html += `</ul>`;
    html += `</div>`;
  }

  if (arquivos.notas_inserir.length > 0) {
    html += `<button class="accordion upload" aria-expanded="false">Amostra notas inseridas( ${arquivos.notas_inserir.length} ultimas )<span class="icon" aria-hidden="true"></span></button>`;
    html += `<div class="panel display-none">`;
    html += `<pre>${JSON.stringify(arquivos.notas_inserir, null, 2)}</pre>`;
    html += `</div>`;
  }
  return html;
}

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
  contadorArquivosDiv.classList.add("display-none");
  if (selectedFiles.length > 0) {
    contadorArquivosDiv.classList.remove("display-none");
    contArchivesHtml.innerHTML = `Total de arquivos selecionados: <strong>${selectedFiles.length}</strong>`;
  }
}

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

cleanUploadButton.addEventListener("click", () => {
  selectedFiles.length = 0;
  renderFileList();
});

export { renderArquivosEnviados, getSelectedFiles };

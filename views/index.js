const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const invalidArchive = document.getElementById('invalid-archiv');
const selectFilesButton = document.getElementById('select-files');
const selectedFiles = [];
const arquivosInvalidos = [];

selectFilesButton.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    for (let file of fileInput.files) {
        if (file.type !== 'text/xml' && file.type !== 'application/xml') {
            arquivosInvalidos.push(file.name);
            continue;
        }
        selectedFiles.push(file);
    }
    renderInvalidFiles();
    renderFileList();
});

function renderInvalidFiles() {
    invalidArchive.innerHTML = '';
    const div = document.createElement('div');
    div.id = "invalid-files-message";
    if (arquivosInvalidos.length !== 0) {
        const p = document.createElement('strong');
        const validos = document.createElement('p');
        p.textContent = `Você selecionou ${arquivosInvalidos.length} arquivo(s) inválido(s). Apenas arquivos XML são permitidos.`;
        if (selectedFiles.length > 0) {
            validos.textContent = `Os ${selectedFiles.length} arquivos válidos foram mantidos.`;
        }
        const okButton = document.createElement('button');
        okButton.textContent = "OK";
        okButton.style.marginLeft = "10px";
        okButton.onclick = () => {
            arquivosInvalidos.length = 0;
            invalidArchive.innerHTML = '';
            invalidArchive.style.padding = "0px";
        }
        div.appendChild(p);
        div.appendChild(validos)
        invalidArchive.appendChild(div);
        invalidArchive.appendChild(okButton);
        invalidArchive.style.padding = "8px";
    }
}

function renderFileList() {
    fileList.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const li = document.createElement('li');
        li.textContent = file.name + " ";
        const removeBtn = document.createElement('button');
        removeBtn.textContent = "X";
        removeBtn.style.marginLeft = "10px";
        removeBtn.onclick = () => {
            selectedFiles.splice(index, 1);
            renderFileList();
        };
        li.appendChild(removeBtn);
        fileList.appendChild(li);
    });
}

function formataDocumentoViews(doc){
    const docLimpo = String(doc).replace(/\D/g, '');
    if (docLimpo.length === 11) {
        return docLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    } else if (docLimpo.length === 14) {
        return docLimpo.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    }

    return doc;
}

function formataDocumentoApp(doc) {
    const docLimpo = String(doc).replace(/\D/g, '');
    if (docLimpo.length === 11) {
        return docLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1$2$3$4');
    } else if (docLimpo.length === 14) {
        return docLimpo.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1$2$3$4$5');
    }

    return doc;
}


document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();    
    const formData = new FormData();

    selectedFiles.forEach(file => {
        formData.append("files", file);
    });

    try {
        const response = await fetch('/notas/upload-lote', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        document.getElementById('response').innerText = JSON.stringify(result, null, 2);
    } catch (error) {
        document.getElementById('response').innerText = 'Erro ao enviar: ' + error.message;
    }
});

document.getElementById('consulta-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const documento = formataDocumentoApp(event.target.documento.value);
    try {
        const response = await fetch(`/consulta/${documento}`);
        if (!response.ok) {
            throw new Error('Nota não encontrada');
        }
        const nota = await response.json();
        let data_emissao = new Date(nota.data_emissao).toLocaleDateString('pt-BR', );

        let mascara_doc = formataDocumentoViews(nota.documento);

        const html = "<h1>Nota Fiscal</h1>" +
                     "<p><strong>Chave de Acesso: </strong> " + nota.chave_acesso + "</p>" +
                     "<p><strong>Destinatário: </strong> " + nota.cliente + "</p>" +
                     "<p><strong>Documento cliente: </strong> " + mascara_doc + "</p>"+
                     "<p><strong>Data de Emissão: </strong> " + data_emissao + "</p>"+
                     "<p><strong>Transportadora: </strong> " + nota.transportadora + "</p>";


        document.getElementById('consulta-response').innerHTML = html;
    } catch (error) {
        document.getElementById('consulta-response').innerText = 'Erro: ' + error.message;
    }
});

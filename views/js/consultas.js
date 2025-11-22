import { formataDocumentoViews } from "./utils.js";

function textoNotaUnica(arquivo) {
  return (
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
    arquivo.cnpj_emitente +
    "</p>" +
    "<p><strong>Destinatário: </strong> " +
    arquivo.cliente +
    "</p>" +
    "<p><strong>Documento cliente: </strong> " +
    arquivo.documento +
    "</p>" +
    "<p><strong>Data de Emissão: </strong> " +
    arquivo.data_emissao +
    "</p>" +
    "<p><strong>Transportadora: </strong> " +
    arquivo.transportadora +
    "</p>" +
    "<p><strong>Valor NF: </strong> " +
    arquivo.valor +
    "</p>" +
    "<p><strong>Mensagem: </strong> " +
    arquivo.mensagem +
    "</p>"
  );
}

function textoNotasMultiplas(arquivo) {
  return (
    `<button class="accordion find">Nota nº ${arquivo.numero_nota} <span class="icon" aria-hidden="true"></span></button>` +
    `<div class="panel display-none">` +
    `<h2>Detalhes da Nota: </h2>` +
    `<p><strong>Chave de Acesso: </strong> ${arquivo.chave_acesso}</p>` +
    `<p><strong>Numero da NF: </strong> ${arquivo.numero_nota}</p>` +
    `<p><strong>Empresa emitente: </strong> ${arquivo.nome_emitente}</p>` +
    `<p><strong>CNPJ emitente: </strong> ${arquivo.cnpj_emitente}</p>` +
    `<p><strong>Destinatário: </strong> ${arquivo.cliente}</p>` +
    `<p><strong>Documento cliente: </strong> ${arquivo.documento}</p>` +
    `<p><strong>Data de Emissão: </strong> ${arquivo.data_emissao}</p>` +
    `<p><strong>Transportadora: </strong> ${arquivo.transportadora}</p>` +
    `<p><strong>Valor NF: </strong> ${arquivo.valor}</p>` +
    `<p><strong>Mensagem: </strong> ${arquivo.mensagem}</p>` +
    `</div>`
  );
}

function formataDadosNotasEncontradas(arquivo) {
  let data_emissao = new Date(arquivo.data_emissao).toLocaleString("pt-BR", {
    timeZone: "America/Sao_Paulo",
    day: "numeric",
    month: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  let valor = Number.isInteger(arquivo.valor)
    ? arquivo.valor.toLocaleString("pt-BR", {
        currency: "BRL",
        style: "currency",
      })
    : "Valor não definido";

  arquivo.cnpj_emitente = formataDocumentoViews(arquivo.cnpj_emitente);
  arquivo.documento = formataDocumentoViews(arquivo.documento);
  arquivo.data_emissao = data_emissao;
  arquivo.valor = valor;

  return arquivo;
}

function renderTextoArquivoEncontrado(arquivo = {}, multiplasNotas = false) {
  arquivo = formataDadosNotasEncontradas(arquivo);
  if (!multiplasNotas) {
    return textoNotaUnica(arquivo);
  }
  return textoNotasMultiplas(arquivo);
}

function renderArquivoEncontrado(arquivos) {
  let html = "";
  if (arquivos.length <= 0) {
    document.getElementById("consulta-response").innerHTML =
      "<p>Nenhuma nota encontrada para este documento.</p>";
    return;
  }
  html +=
    arquivos.length > 1
      ? `<h1>Notas Fiscais Encontradas: ${arquivos.length}</h1>`
      : "";
  for (const arquivo of arquivos) {
    html += renderTextoArquivoEncontrado(arquivo, arquivos.length > 1);
  }
  return html;
}

export { renderArquivoEncontrado };

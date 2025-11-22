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

function mostraHTML(objetoHTML) {
  objetoHTML.classList.remove("display-none");
}

function escondeHTML(objetoHTML) {
  objetoHTML.classList.add("display-none");
}

export { formataDocumentoViews, formataDocumentoApp, mostraHTML, escondeHTML };

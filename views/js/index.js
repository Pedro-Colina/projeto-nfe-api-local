import { renderArquivoEncontrado } from "./consultas.js";
import { formataDocumentoApp } from "./utils.js";
import { renderArquivosEnviados, getSelectedFiles } from "./uploads.js";
import { mostraLoading, escondeLoading } from "./loading.js";

const loading = document.getElementById("loading");

function adicionaAccordeon(className = "") {
  const accordions = document.querySelectorAll(".accordion" + className);
  for (const accordion of accordions) {
    accordion.addEventListener("click", function () {
      this.classList.toggle("active");
      this.getElementsByClassName("icon")[0].classList.toggle("active");
      const panel = this.nextElementSibling;
      panel.classList.toggle("display-none");
    });
  }
}

document
  .getElementById("upload-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    mostraLoading();
    const formData = new FormData();

    for (const file of getSelectedFiles()) {
      formData.append("files", file);
    }

    try {
      const response = await fetch("/notas/upload-lote", {
        method: "POST",
        body: formData,
      });
      const result = await response.json();
      escondeLoading();
      document.getElementById("response").innerHTML =
        renderArquivosEnviados(result);
      adicionaAccordeon(".upload");
    } catch (error) {
      escondeLoading();
      document.getElementById("response").innerText =
        "Erro ao enviar: " + error.message;
    }
  });

document
  .getElementById("consulta-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();
    mostraLoading();
    const documento = formataDocumentoApp(event.target.documento.value);
    try {
      const response = await fetch(`/consulta?documento=${documento}`);
      if (!response.ok) {
        throw new Error("Nota há notas fiscais para este documento.");
      }
      const nota = await response.json();
      escondeLoading();
      document.getElementById("consulta-response").innerHTML =
        renderArquivoEncontrado(nota);
      adicionaAccordeon(".find");
    } catch (error) {
      escondeLoading();
      document.getElementById("consulta-response").innerText =
        "Erro: " + error.message;
    }
  });

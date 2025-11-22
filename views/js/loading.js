import { mostraHTML, escondeHTML } from "./utils.js";
const loading = document.getElementById("loading");

function mostraLoading() {
  mostraHTML(loading);
}

function escondeLoading() {
  escondeHTML(loading);
}

export { mostraLoading, escondeLoading };

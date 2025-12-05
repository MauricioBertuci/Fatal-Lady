const calculateShippingButton = document.getElementById("calculate-shipping-btn");
const shippingResults = document.getElementById("shipping-results");
const enderecoElement = document.getElementById("endereco");
const valorFreteElement = document.getElementById("valor_frete");
const prazoElement = document.getElementById("prazo");
const subtotalElement = document.getElementById("subtotal");
const totalElement = document.getElementById("total");
const cepHidden = document.getElementById("cepHidden");
const enderecoHidden = document.getElementById("enderecoHidden");
const freteHidden = document.getElementById("freteHidden");
const totalHidden = document.getElementById("totalHidden");

function normalizeNumber(value) {
  if (value == null) return 0;
  const text = String(value)
    .replace(/\s/g, "")
    .replace(/[^0-9.,-]/g, "")
    .replace(",", ".");
  const n = parseFloat(text);
  return isNaN(n) ? 0 : n;
}

if (calculateShippingButton) {
  calculateShippingButton.addEventListener("click", async () => {
    const cepInput = document.getElementById("cep-input");
    if (!cepInput) return;

    const cep = cepInput.value.replace(/\D/g, ""); // só números

    if (cep.length !== 8) {
      alert("Digite um CEP válido com 8 dígitos.");
      return;
    }

    try {
      const response = await fetch(`/frete/calcular/?cep_destino=${cep}`, {
  method: "GET",
  credentials: "include",   // <- ESSENCIAL pra enviar o cookie "token"
});

    

      if (!response.ok) throw new Error("Erro ao consultar o frete.");

      const data = await response.json();
      console.log("Resposta frete:", data);

      // frete em número, independente se veio "12.34", "12,34" ou "R$ 12,34"
      const frete = normalizeNumber(data.valor_frete);
      console.log("Frete normalizado:", frete);

      if (shippingResults) shippingResults.style.display = "block";
      if (enderecoElement) enderecoElement.innerText = data.endereco || "";
      if (valorFreteElement) valorFreteElement.innerText = frete.toFixed(2);
      if (prazoElement) prazoElement.innerText = data.prazo_estimado_dias || "";

      // subtotal atual da página
      let subtotal = 0;
      if (subtotalElement) {
        const textSubtotal =
          subtotalElement.innerText || subtotalElement.textContent || "";
        subtotal = normalizeNumber(textSubtotal);
      }
      console.log("Subtotal:", subtotal);

      const totalCalc = subtotal + frete;
      console.log("Total calculado:", totalCalc);

      if (totalElement) totalElement.innerText = `R$ ${totalCalc
        .toFixed(2)
        .replace(".", ",")}`;

      if (cepHidden) cepHidden.value = cep;
      if (enderecoHidden) enderecoHidden.value = data.endereco || "";
      if (freteHidden) freteHidden.value = frete.toFixed(2);
      if (totalHidden) totalHidden.value = totalCalc.toFixed(2);
    } catch (error) {
      console.error("Erro ao calcular frete:", error);
      alert("Erro ao calcular o frete. Tente novamente.");
    }
  });
}

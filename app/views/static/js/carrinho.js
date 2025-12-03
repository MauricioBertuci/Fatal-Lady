// Arquivo: /static/js/carrinho.js
// DEVE SER CARREGADO APENAS EM 'carrinho.html'

document.addEventListener("DOMContentLoaded", () => {
  // --- FUNÇÃO PRINCIPAL: CALCULA ITENS E SALVA NO LOCALSTORAGE ---
  const updateLocalStorageCount = () => {
    // Seletores precisam estar corretos: .cart-item e .input-quantity
    const allItems = document.querySelectorAll(".cart-item");
    let totalCount = 0;

    if (allItems.length > 0) {
      allItems.forEach((item) => {
        const qtyInput = item.querySelector(".input-quantity");
        if (qtyInput) {
          totalCount += parseInt(qtyInput.value, 10) || 0;
        }
      });
    }

    // Salva o total calculado. Isso faz a chave 'cartItemCount' aparecer.
    localStorage.setItem("cartItemCount", totalCount);

    // Notifica o badge global (cart-badge.js) para atualizar imediatamente.
    window.dispatchEvent(new Event("cartUpdated"));
  };

  // 1. Calcula e salva o total assim que a página do carrinho carregar
  updateLocalStorageCount();

  // --- LÓGICA DE FORMULÁRIO (Formulários de update) ---
  const updateForms = document.querySelectorAll(".form-update-cart");

  updateForms.forEach((form) => {
    const qtyInput = form.querySelector(".input-quantity");
    const btnMinus = form.querySelector(".btn-qty-minus");
    const btnPlus = form.querySelector(".btn-qty-plus");

    const submitForm = () => {
      const cartItem = form.closest(".cart-item");
      if (cartItem) {
        // Feedback visual enquanto espera o reload
        cartItem.classList.add("removing");
      }
      // O submit() causa o reload da página, onde 'updateLocalStorageCount' roda novamente.
      form.submit();
    };

    if (btnPlus) {
      btnPlus.addEventListener("click", () => {
        qtyInput.value = parseInt(qtyInput.value, 10) + 1;
        submitForm();
      });
    }

    if (btnMinus) {
      btnMinus.addEventListener("click", () => {
        let currentValue = parseInt(qtyInput.value, 10);
        if (currentValue > 1) {
          qtyInput.value = currentValue - 1;
          submitForm();
        }
      });
    }

    if (qtyInput) {
      qtyInput.addEventListener("change", () => {
        let currentValue = parseInt(qtyInput.value, 10);
        if (currentValue < 1 || isNaN(currentValue)) {
          qtyInput.value = 1;
        }
        submitForm();
      });
    }
  });

  // ===============================
  // CEP OBRIGATÓRIO + LOADING CHECKOUT
  // ===============================

  function getCepDigits() {
    const cepInput = document.getElementById("cep-input");
    if (!cepInput) return "";
    return cepInput.value.replace(/\D/g, "");
  }

  function showCepError() {
    const cepInput = document.getElementById("cep-input");
    if (!cepInput) return;

    cepInput.classList.add("input-error");
    cepInput.focus();
  }

  const checkoutForm = document.getElementById("form-carrinho");
  const checkoutButton = checkoutForm
    ? checkoutForm.querySelector(".btn-checkout")
    : null;

  if (checkoutForm && checkoutButton) {
    checkoutForm.addEventListener("submit", (e) => {
      const cepDigits = getCepDigits();

      // CEP precisa ser válido (8 dígitos)
      if (cepDigits.length !== 8) {
        e.preventDefault();
        showCepError();
        return;
      }

      // evita submit duplo
      if (checkoutButton.disabled) {
        e.preventDefault();
        return;
      }

      // Ativa loading no botão
      checkoutButton.disabled = true;
      checkoutButton.classList.add("btn-loading");
    });
  }
});

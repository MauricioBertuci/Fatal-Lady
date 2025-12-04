document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll(".favorite-toggle-form");

  if (!forms.length) return;

  forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const button = form.querySelector(".favorite-toggle-btn");
      if (!button || button.disabled) return;

      button.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: form.method || "POST",
          body: new FormData(form),
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });

        // Se o back-end responder 200/204, só inverte o estado visual
        if (response.ok) {
          button.classList.toggle("is-favorite");
        } else if (response.status === 401 || response.status === 403) {
          // não autenticado, volta comportamento padrão para essa tentativa
          window.location.href = "/login";
        } else {
          console.warn("Falha ao favoritar, status:", response.status);
        }
      } catch (error) {
        console.error("Erro ao favoritar:", error);
      } finally {
        button.disabled = false;
      }
    });
  });
});

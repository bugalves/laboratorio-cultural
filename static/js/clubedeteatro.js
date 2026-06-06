

function toggleBook(button) {
  const card = button.closest(".book-card")

  card.classList.toggle("active")

  if (card.classList.contains("active")) {
    button.innerHTML = "Mostrar menos ▲"
  } else {
    button.innerHTML = "Saber mais ▼"
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".join-form");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      alert("Inscrição realizada com sucesso!");

      this.reset();
    });
  }
});

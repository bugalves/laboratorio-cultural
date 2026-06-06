function toggleBook(button) {
  const card = button.closest(".book-card");
  const details = card.querySelector(".book-details");

  // Fecha todos os outros
  document.querySelectorAll(".book-card").forEach(c => {
    if (c === card) return;
    c.querySelector(".book-details").style.display = "none";
    c.querySelector("button").innerHTML = "Saber mais ▼";
  });

  // Toggle só neste
  if (details.style.display === "block") {
    details.style.display = "none";
    button.innerHTML = "Saber mais ▼";
  } else {
    details.style.display = "block";
    button.innerHTML = "Mostrar menos ▲";
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


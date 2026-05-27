

function toggleBook(button) {
  const card = button.closest(".book-card")

  card.classList.toggle("active")

  if (card.classList.contains("active")) {
    button.innerHTML = "Mostrar menos ▲"
  } else {
    button.innerHTML = "Saber mais ▼"
  }
}





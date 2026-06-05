function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1]
}

function toggleEvent(btn) {
  const card = btn.closest(".event-card")
  const details = card.querySelector(".event-details")

  if (details.style.display === "block") {
    details.style.display = "none"
    btn.innerText = "Ver detalhes ▼"
  } else {
    details.style.display = "block"
    btn.innerText = "Ocultar detalhes ▲"
  }
}

function inscrever(btn) {
  const card = btn.closest(".event-card")

  const id = card.dataset.eventId
  const tipo = card.dataset.eventType

  if (!isAuthenticated) {
    window.location.href = "/login?next=/programacaocultural/"
    return
  }

  fetch("/api/inscrever", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      tipo,
      id,
    }),
  })
    .then((res) => {
      if (!res.ok) throw new Error("Erro na inscrição")
      return res.json()
    })
    .then((data) => {
      location.reload()
    })
    .catch((err) => {
      console.error(err)
      alert("Erro ao inscrever no evento.")
    })
}

async function cancelarInscricao(btn) {
  const inscricaoId = btn.dataset.id

  const confirmar = confirm("Tem a certeza que pretende cancelar a inscrição?")

  if (!confirmar) {
    return
  }

  try {
    const response = await fetch(`/api/inscricoes/${inscricaoId}`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || "Erro ao cancelar inscrição")
    }

    const card = btn.closest(".inscricao-card")

    card.remove()

    setTimeout(() => {
      location.reload()
    }, 300)
  } catch (error) {
    alert(error.message)
  }
}

async function atualizarPerfil(e) {
  e.preventDefault()

  const email = document.getElementById("emailInput").value
  const password = document.getElementById("passwordInput").value

  const response = await fetch("/api/user", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })

  const data = await response.json()

  if (data.success) {
    alert("Perfil atualizado.")
  }
}

function toggleProfileMenu() {
  document.getElementById("profileDropdown").classList.toggle("active")
}

function openInscricoesModal() {
  document.getElementById("inscricoesModal").classList.add("active")
}

function closeInscricoesModal() {
  document.getElementById("inscricoesModal").classList.remove("active")
}

function openPerfilModal() {
  document.getElementById("perfilModal").classList.add("active")
}

function closePerfilModal() {
  document.getElementById("perfilModal").classList.remove("active")
}

document.addEventListener("DOMContentLoaded", function () {

  // ================= NAV HEIGHT =================
  const nav = document.querySelector("nav")

  if (nav) {
    const observer = new ResizeObserver((entries) => {
      const height = entries[0].contentRect.height
      document.documentElement.style.setProperty("--nav-height", `${height}px`)
    })

    observer.observe(nav)
  }

  // ================= CALENDAR =================
  const calendarEl = document.getElementById("calendar")
  if (!calendarEl) return

  const eventsUrl = calendarEl.dataset.eventsUrl

  // ================= CALENDAR MODAL (ISOLADO) =================
  const modal = document.getElementById("calendar-event-modal")
  const modalTitle = document.getElementById("modal-title")
  const modalDate = document.getElementById("modal-date")
  const modalDescription = document.getElementById("modal-description")
  const modalClose = document.getElementById("calendar-modal-close")

  function openModal(event) {

    modalTitle.textContent = event.title || "Sem título"

    modalDate.textContent = event.start
      ? new Date(event.start).toLocaleDateString("pt-PT")
      : "Sem data"

    modalDescription.textContent =
      event.extendedProps?.description || "Sem descrição"

    const localEl = document.getElementById("modal-local")
    const cidadeEl = document.getElementById("modal-cidade")
    const vagasEl = document.getElementById("modal-vagas")
    const btn = document.getElementById("modal-participar")

    if (localEl) localEl.textContent = event.extendedProps?.local || "-"
    if (cidadeEl) cidadeEl.textContent = event.extendedProps?.cidade || "-"

      if (vagasEl) {
        vagasEl.textContent =
          event.extendedProps?.vagas_restantes ?? "-"
      }

    if (btn) {
      btn.dataset.id = event.id
      btn.dataset.tipo = event.extendedProps?.tipo
    }

    modal.classList.remove("hidden")
  }

  function closeModal() {
    modal.classList.add("hidden")
  }

  if (modalClose) {
    modalClose.addEventListener("click", closeModal)
  }

  window.addEventListener("click", function (e) {
    if (e.target === modal) closeModal()
  })

  // ================= FULLCALENDAR =================
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    locale: "pt",
    events: eventsUrl,

    eventClick: function (info) {
      info.jsEvent.preventDefault()
      openModal(info.event)
    },

    eventBackgroundColor: "#c62828",
    eventBorderColor: "#c62828",
    eventTextColor: "#fff",
  })

  calendar.render()
})


document.addEventListener("click", function (e) {

  const btn = e.target.closest("#modal-participar")
  if (!btn) return

  const id = btn.dataset.id
  const tipo = btn.dataset.tipo

  fetch(`/participar/${tipo}/${id}/`, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCSRFToken()
    }
  })
  .then(res => res.json())
  .then(data => {

    if (data.success) {
      alert("Inscrição feita com sucesso!")

      const vagasEl = document.getElementById("modal-vagas")
      if (vagasEl && data.vagas_restantes !== undefined) {
        vagasEl.textContent = data.vagas_restantes
      }

    } 
    else if (data.already) {
      alert("Já estás inscrito nesta atividade.")
    } 
    else {
      alert(data.error || "Erro ao inscrever")
    }

  })
  .catch(err => {
    console.error(err)
    alert("Tem que estar autenticado para se inscrever.")
  })

})

function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    ?.split("=")[1]
}
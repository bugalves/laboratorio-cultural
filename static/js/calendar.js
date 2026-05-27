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

  // ================= MODAL =================
  const modal = document.getElementById("event-modal")
  const modalTitle = document.getElementById("modal-title")
  const modalDate = document.getElementById("modal-date")
  const modalDescription = document.getElementById("modal-description")
  const modalClose = document.getElementById("modal-close")

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
      const restantes =
        (event.extendedProps?.vagas || 0) -
        (event.extendedProps?.inscritos || 0)

      vagasEl.textContent = restantes >= 0 ? restantes : 0
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


// ================= PARTICIPAR =================
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

      document.getElementById("modal-vagas").textContent =
        data.vagas_restantes

    } else {
      alert(data.error || "Erro ao inscrever")
    }
  })
})

function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find(row => row.startsWith("csrftoken="))
    ?.split("=")[1]
}


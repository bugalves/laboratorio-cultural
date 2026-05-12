const nav = document.querySelector('nav');

const observer = new ResizeObserver(entries => {
  const height = entries[0].contentRect.height;
  document.documentElement.style.setProperty('--nav-height', `${height}px`);
});

observer.observe(nav);

document.addEventListener('DOMContentLoaded', function() {

    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {

        initialView: 'dayGridMonth',

        locale: 'pt',

        events: '/api/eventos/',

        eventBackgroundColor: '#c62828',
        eventBorderColor: '#c62828',
        eventTextColor: '#fff',

        eventClick: function(info){

            document.getElementById('modalTitle').innerText =
                info.event.title;

            document.getElementById('modalDate').innerText =
                info.event.start.toLocaleDateString();

            document.getElementById('modalLocation').innerText =
                info.event.extendedProps.location || '';

            document.getElementById('modalDescription').innerText =
                info.event.extendedProps.description || '';

            document.getElementById('modalImage').src =
                info.event.extendedProps.image || '';

            document.getElementById('eventModal').style.display = 'block';
        }

    });

    calendar.render();

    // FECHAR MODAL

    document.querySelector('.close-modal').onclick = function(){

        document.getElementById('eventModal').style.display = 'none';

    }

    // FECHAR AO CLICAR FORA

    window.onclick = function(event){

        const modal = document.getElementById('eventModal');

        if(event.target == modal){

            modal.style.display = 'none';

        }

    }

});

function toggleBook(button){

      const card = button.closest('.book-card');

      card.classList.toggle('active');

      if(card.classList.contains('active')){
        button.innerHTML = 'Mostrar menos ▲';
      }else{
        button.innerHTML = 'Saber mais ▼';
      }

    }
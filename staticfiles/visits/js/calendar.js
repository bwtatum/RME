document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");
  if (!calendarEl) return;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    height: "auto",
    nowIndicator: true,
    navLinks: true,

    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
    },

    events: calendarEl.dataset.eventsUrl,

    eventTimeFormat: {
      hour: "2-digit",
      minute: "2-digit",
      meridiem: true
    },

    eventClick: function (info) {
      if (info.event.url) {
        info.jsEvent.preventDefault();
        window.location.href = info.event.url;
      }
    }
  });

  calendar.render();
});
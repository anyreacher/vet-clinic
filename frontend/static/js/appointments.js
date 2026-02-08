
const doctorSelect = document.getElementById('doctor-select');
const scheduleMessage = document.getElementById('schedule-message');
const scheduleGrid = document.getElementById('schedule-grid');

const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const SLOT_TIMES = [];
for (let h = 9; h < 17; h++) {
  SLOT_TIMES.push(String(h).padStart(2, '0') + ':00');
  SLOT_TIMES.push(String(h).padStart(2, '0') + ':30');
}

function getWeekStart(d) {
  d = new Date(d);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  return new Date(d.setDate(diff));
}

function toISODate(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return y + '-' + m + '-' + day;
}

function showMessage(text, isError) {
  scheduleMessage.textContent = text;
  scheduleMessage.hidden = !text;
  if (scheduleMessage.classList) {
    scheduleMessage.classList.toggle('error', isError !== false);
  }
}

function buildSlotsByDay(slots) {
  const byDay = {};
  slots.forEach(function(s) {
    const start = new Date(s.start);
    const dateKey = toISODate(start);
    const timeKey = String(start.getHours()).padStart(2, '0') + ':' + String(start.getMinutes()).padStart(2, '0');
    if (!byDay[dateKey]) byDay[dateKey] = {};
    byDay[dateKey][timeKey] = { start: s.start, booked: s.booked };
  });
  return byDay;
}

function renderGrid(doctorId, weekStart, slotsByDay) {
  scheduleGrid.hidden = false;
  scheduleGrid.replaceChildren();

  const firstCol = document.createElement('div');
  firstCol.className = 'day-label';
  firstCol.textContent = 'Time';
  scheduleGrid.appendChild(firstCol);

  const weekStartDate = new Date(weekStart);
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStartDate);
    d.setDate(weekStartDate.getDate() + i);
    const th = document.createElement('div');
    th.className = 'day-label';
    th.textContent = DAY_NAMES[i] + ' ' + toISODate(d).slice(5);
    scheduleGrid.appendChild(th);
  }

  const dayDates = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStartDate);
    d.setDate(weekStartDate.getDate() + i);
    dayDates.push(toISODate(d));
  }

  SLOT_TIMES.forEach(function(timeStr) {
    const timeLabel = document.createElement('div');
    timeLabel.className = 'day-label';
    timeLabel.textContent = timeStr;
    scheduleGrid.appendChild(timeLabel);

    for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
      const dateKey = dayDates[dayIndex];
      const daySlots = slotsByDay[dateKey];
      const slotInfo = daySlots && daySlots[timeStr];
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'slot';
      cell.textContent = slotInfo ? (slotInfo.booked ? '—' : 'Book') : '—';
      if (slotInfo && slotInfo.booked) {
        cell.classList.add('booked');
        cell.disabled = true;
      } else if (slotInfo) {
        cell.dataset.start = slotInfo.start;
        cell.addEventListener('click', function() {
          bookSlot(doctorId, slotInfo.start, cell);
        });
      } else {
        cell.disabled = true;
      }
      scheduleGrid.appendChild(cell);
    }
  });
}

function bookSlot(doctorId, startTime, buttonEl) {
  buttonEl.disabled = true;
  showMessage('Booking…', false);
  window.auth.fetchApi('/appointments', {
    method: 'POST',
    body: JSON.stringify({ doctor_id: doctorId, start_time: startTime })
  })
    .then(function() {
      showMessage('Booked. Updating…', false);
      loadSlots();
    })
    .catch(function(err) {
      buttonEl.disabled = false;
      showMessage(err.message || 'Booking failed', true);
    });
}

function loadSlots() {
  const doctorId = doctorSelect.value;
  if (!doctorId) {
    scheduleGrid.hidden = true;
    scheduleMessage.hidden = true;
    return;
  }
  const weekStart = getWeekStart(new Date());
  const weekStartStr = toISODate(weekStart);
  showMessage('Loading…', false);
  scheduleGrid.hidden = true;

  window.auth.fetchApi('/appointments/slots?doctor_id=' + encodeURIComponent(doctorId) + '&week_start=' + encodeURIComponent(weekStartStr))
    .then(function(data) {
      showMessage('', false);
      const slotsByDay = buildSlotsByDay(data.slots);
      renderGrid(parseInt(doctorId, 10), weekStartStr, slotsByDay);
    })
    .catch(function(err) {
      showMessage(err.message || 'Failed to load schedule', true);
    });
}

if (!window.auth || !window.auth.getToken()) {
  window.location.href = 'login.html';
  return;
}

window.auth.fetchApi('/appointments/doctors')
  .then(function(doctors) {
    doctors.forEach(function(d) {
      const opt = document.createElement('option');
      opt.value = d.id;
      opt.textContent = d.name + (d.specialty ? ' — ' + d.specialty : '');
      doctorSelect.appendChild(opt);
    });
  })
  .catch(function() {
    showMessage('Failed to load specialists', true);
  });

doctorSelect.addEventListener('change', loadSlots);


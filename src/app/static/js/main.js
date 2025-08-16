/* ========= Config ========= */
const API_URL = '/api/v1/tasks/';

const statusToLabel = {
  not_started: 'Not Started',
  in_progress: 'In Progress',
  blocked: 'Blocked',
  completed: 'completed',
};

const statusToPanelId = {
  not_started: 'queue-panel',
  in_progress: 'serving-panel',
  blocked: 'completed-panel',
  completed: 'cancelled-panel',
};

const panelIdToStatus = {
  'queue-panel': 'not_started',
  'serving-panel': 'in_progress',
  'completed-panel': 'blocked',
  'cancelled-panel': 'completed',
};

/* ========= Utilidades ========= */
function getColumnByStatus(status) {
  const panelId = statusToPanelId[status] || statusToPanelId.not_started;
  return document.querySelector(`#${panelId} .kanban-column`);
}

function getStatusByColumnEl(columnEl) {
  const panel = columnEl?.closest('.tab-pane');
  return panelIdToStatus[panel?.id] || 'not_started';
}

function priorityLabel(num) {
  if (num === 1) return 'Low';
  if (num === 2) return 'Medium';
  if (num === 3) return 'High';
  return 'Unknown';
}

function priorityBadgeClass(num) {
  // Bootstrap 5: azul=primary, amarillo=warning, rojo=danger
  if (num === 1) return 'text-bg-primary'; // Low -> azul
  if (num === 2) return 'text-bg-warning'; // Medium -> amarillo
  if (num === 3) return 'text-bg-danger';  // High -> rojo
  return 'text-bg-secondary';
}

function formatDateYMDToDMY(isoDate) {
  if (!isoDate) return '-';
  const d = new Date(isoDate + 'T00:00:00');
  if (isNaN(d)) return isoDate;
  const dd = String(d.getDate()).padStart(2, '0');
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${dd}/${mm}/${yyyy}`;
}

function escapeHTML(str) {
  return String(str ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

/* ========= Menú dinámico ========= */
function buildMoveMenuHTML(currentStatus, taskId) {
  return Object.keys(statusToLabel)
    .filter(s => s !== currentStatus)
    .map(s => `<a class="dropdown-item" href="#" data-move-to="${s}" data-task-id="${taskId}">Move to ${statusToLabel[s]}</a>`)
    .join('');
}

function refreshCardMenu(card) {
  const currentStatus = card.dataset.status || 'not_started';
  const id = card.dataset.id;
  const menu = card.querySelector('.dropdown-menu');
  if (!menu) return;

  menu.innerHTML = `
    ${buildMoveMenuHTML(currentStatus, id)}
    <div class="dropdown-divider"></div>
    <a class="dropdown-item" href="#"><strong>Details</strong></a>
  `;
}

function setCardStatus(card, newStatus) {
  card.dataset.status = newStatus;
  refreshCardMenu(card);
}

/* ========= Tarjeta ========= */
function createTaskHTML(task) {
  const id = task.id;
  const title = escapeHTML(task.title || 'Untitled');
  const due = formatDateYMDToDMY(task.due_date);
  const subject = escapeHTML(task.subject || '-');
  const priorityTxt = priorityLabel(task.priority);
  const priorityCls = priorityBadgeClass(task.priority);
  const status = task.status || (task.completed ? 'completed' : 'not_started');

  return `
  <div class="card mb-2 kanban-card" draggable="true" data-id="${id}" data-status="${status}" ondragstart="drag(event)">
    <div class="card-body">
      <div class="d-flex justify-content-between">
        <h5 class="text-muted mb-2">${title}</h5>
        <div class="dropdown">
          <button class="btn btn-sm dropdown-toggle" aria-expanded="false" data-bs-toggle="dropdown" type="button" aria-haspopup="true"></button>
          <div class="dropdown-menu dropdown-menu-end">
            ${buildMoveMenuHTML(status, id)}
            <div class="dropdown-divider"></div>
            <a class="dropdown-item" href="#"><strong>Details</strong></a>
          </div>
        </div>
      </div>
      <div class="info mb-2"><strong><span> Due Date:</span></strong><span> ${due}</span></div>
      <div class="info mb-2"><strong><span> Subject:</span></strong><span> ${subject}</span></div>
      <div>
        <span class="badge rounded-pill ${priorityCls}" style="font-size:0.9em;">${priorityTxt}</span>
      </div>
    </div>
  </div>`;
}

/* ========= Carga & render ========= */
async function loadTasks() {
  // Limpia todas las columnas (incluye la tarjeta de ejemplo)
  document.querySelectorAll('.kanban-column').forEach(col => (col.innerHTML = ''));

  try {
    const resp = await fetch(API_URL, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'include', // importante para enviar la cookie de sesión
    });

    if (!resp.ok) {
      console.error('HTTP error', resp.status);
      alert('No se pudieron cargar las tareas.');
      return;
    }

    const json = await resp.json();
    const tasks = json?.data?.tasks ?? [];

    tasks.forEach(t => {
      const status = t.status || (t.completed ? 'completed' : 'not_started');
      const col = getColumnByStatus(status);
      if (!col) return;
      col.insertAdjacentHTML('beforeend', createTaskHTML({ ...t, status }));
    });
  } catch (e) {
    console.error(e);
    alert('Ocurrió un error al traer las tareas.');
  }
}

/* ========= Mover por menú (delegación) ========= */
document.addEventListener('click', (ev) => {
  const item = ev.target.closest('a.dropdown-item[data-move-to]');
  if (!item) return;

  ev.preventDefault();
  const newStatus = item.getAttribute('data-move-to');
  const card = item.closest('.kanban-card');
  if (!card) return;

  const targetCol = getColumnByStatus(newStatus);
  if (!targetCol) return;

  targetCol.appendChild(card);
  setCardStatus(card, newStatus);
});

/* ========= Wrappers GLOBALS para handlers inline =========
   (compatibles con tu otro archivo de DnD) */
window.allowDrop = function(event) {
  event.preventDefault();
};

window.drag = function(event) {
  // Alineado con tu implementación
  event.dataTransfer.setData('text/html', event.currentTarget.outerHTML);
  event.dataTransfer.setData('text/plain', event.currentTarget.dataset.id);
};

window.drop = function(event) {
  // Quita highlight de todas las columnas
  document.querySelectorAll('.kanban-column').forEach(column => column.classList.remove('drop'));

  // Necesario para permitir el drop
  event.preventDefault();

  const id = event.dataTransfer?.getData('text/plain');
  const html = event.dataTransfer?.getData('text/html');
  if (!id || !html) return;

  // Elimina la tarjeta original si existe
  try {
    const original = document.querySelector(`.kanban-card[data-id="${CSS.escape(id)}"]`);
    if (original) original.remove();
  } catch (e) {
    const original = document.querySelector(`.kanban-card[data-id="${id}"]`);
    if (original) original.remove();
  }

  // Inserta la nueva tarjeta en la columna destino
  event.currentTarget.insertAdjacentHTML('beforeend', html);

  // Localiza la tarjeta recién insertada y ajusta su estado + menú
  let newCard;
  try {
    const list = event.currentTarget.querySelectorAll(`.kanban-card[data-id="${CSS.escape(id)}"]`);
    newCard = list[list.length - 1];
  } catch (e) {
    const list = event.currentTarget.querySelectorAll(`.kanban-card[data-id="${id}"]`);
    newCard = list[list.length - 1];
  }

  if (newCard) {
    // Asegura attrs DnD en la tarjeta (por si el HTML inicial no los tenía)
    newCard.setAttribute('draggable', 'true');
    newCard.setAttribute('ondragstart', 'drag(event)');

    // Actualiza status según la columna y refresca menú
    const newStatus = getStatusByColumnEl(event.currentTarget);
    setCardStatus(newCard, newStatus);
  }
};

/* ========= Inicio ========= */
document.addEventListener('DOMContentLoaded', () => {
  loadTasks();
});

// Opcional: expone recarga manual
window.loadTasks = loadTasks;
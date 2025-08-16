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

function setCardBusy(card, isBusy) {
  card.classList.toggle('opacity-50', isBusy); // utilitaria de Bootstrap
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

/* ========= Persistencia (PATCH) ========= */
async function updateTaskStatus(taskId, newStatus) {
  try {
    const resp = await fetch(`${API_URL}${taskId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'include', // envía la cookie de sesión
      body: JSON.stringify({ status: newStatus }),
    });

    // Si tu backend responde con JSON de error, lo capturamos
    let data = null;
    try { data = await resp.json(); } catch (_) { /* puede que no haya body */ }

    if (!resp.ok) {
      const msg = data?.message || `HTTP ${resp.status}`;
      throw new Error(msg);
    }
    return { ok: true, data };
  } catch (err) {
    return { ok: false, error: err.message || String(err) };
  }
}

async function persistCardStatus(card, newStatus, oldStatus) {
  setCardBusy(card, true);
  const taskId = card.dataset.id;
  const res = await updateTaskStatus(taskId, newStatus);
  setCardBusy(card, false);

  if (!res.ok) {
    // Revertir UI
    const oldCol = getColumnByStatus(oldStatus);
    if (oldCol) {
      oldCol.appendChild(card);
      setCardStatus(card, oldStatus);
    }
    alert(`No se pudo actualizar el estado de la tarea #${taskId}: ${res.error}`);
    return false;
  }
  return true;
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
document.addEventListener('click', async (ev) => {
  const item = ev.target.closest('a.dropdown-item[data-move-to]');
  if (!item) return;

  ev.preventDefault();
  const newStatus = item.getAttribute('data-move-to');
  const card = item.closest('.kanban-card');
  if (!card) return;

  const oldStatus = card.dataset.status || 'not_started';
  const targetCol = getColumnByStatus(newStatus);
  if (!targetCol) return;

  // UI optimista
  targetCol.appendChild(card);
  setCardStatus(card, newStatus);

  // Persistir y revertir si falla
  await persistCardStatus(card, newStatus, oldStatus);
});

/* ========= Wrappers GLOBALS para handlers inline =========
   (compatibles con tu otro archivo de DnD) */
window.allowDrop = function(event) {
  event.preventDefault();
};

window.drag = function(event) {
  // Alineado con tu implementación + origen del estado
  event.dataTransfer.setData('text/html', event.currentTarget.outerHTML);
  event.dataTransfer.setData('text/plain', event.currentTarget.dataset.id);
  event.dataTransfer.setData('application/x-from-status', event.currentTarget.dataset.status || 'not_started');
};

window.drop = async function(event) {
  // Quita highlight de todas las columnas
  document.querySelectorAll('.kanban-column').forEach(column => column.classList.remove('drop'));

  // Necesario para permitir el drop
  event.preventDefault();

  const id = event.dataTransfer?.getData('text/plain');
  const html = event.dataTransfer?.getData('text/html');
  const fromStatus = event.dataTransfer?.getData('application/x-from-status') || 'not_started';
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

  // Localiza la tarjeta recién insertada
  let newCard;
  try {
    const list = event.currentTarget.querySelectorAll(`.kanban-card[data-id="${CSS.escape(id)}"]`);
    newCard = list[list.length - 1];
  } catch (e) {
    const list = event.currentTarget.querySelectorAll(`.kanban-card[data-id="${id}"]`);
    newCard = list[list.length - 1];
  }
  if (!newCard) return;

  // Asegura attrs DnD
  newCard.setAttribute('draggable', 'true');
  newCard.setAttribute('ondragstart', 'drag(event)');

  // Actualiza status según la columna y refresca menú
  const newStatus = getStatusByColumnEl(event.currentTarget);
  setCardStatus(newCard, newStatus);

  // Persistir y revertir si falla
  await persistCardStatus(newCard, newStatus, fromStatus);
};

/* ========= Inicio ========= */
document.addEventListener('DOMContentLoaded', () => {
  loadTasks();
});

// Opcional: expone recarga manual
window.loadTasks = loadTasks;

/* ========= Crear tarea ========= */
function getTaskPayloadFromForm(form) {
  const status = form.status.value;
  return {
    title: (form.title.value || '').trim(),
    description: (form.description.value || '').trim(),
    completed: status === 'completed',
    priority: Number(form.priority.value),
    status,
    due_date: form.due_date.value,            // "YYYY-MM-DD"
    subject: (form.subject.value || '').trim(),
    created_at: new Date().toISOString().slice(0, 10), // "YYYY-MM-DD"
    // owner_id: {{ id }}  // <-- Solo si de verdad necesitas enviarlo desde el cliente
  };
}

async function createTask(payload) {
  const resp = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload)
  });

  let data = null;
  try { data = await resp.json(); } catch (_) {}

  if (!resp.ok) {
    const msg = data?.message || `HTTP ${resp.status}`;
    throw new Error(msg);
  }
  return data;
}

/* ========= Toast helper ========= */
function showToast(message, variant = 'success', delay = 1500) {
  const toastEl = document.getElementById('globalToast');
  if (!toastEl) { alert(message); return; }
  toastEl.classList.remove('bg-success','bg-danger','bg-warning','bg-info','bg-primary','bg-secondary','bg-dark');
  toastEl.classList.add(`bg-${variant}`);
  toastEl.querySelector('.toast-body').textContent = message;

  const toast = bootstrap.Toast.getOrCreateInstance(toastEl, { delay });
  toast.show();
}

/* ========= Submit del formulario ========= */
async function handleCreateTaskSubmit(ev) {
  ev.preventDefault();
  const form = ev.currentTarget;

  // Validación nativa de BS5
  if (!form.checkValidity()) {
    form.classList.add('was-validated');
    return;
  }

  const btn = document.getElementById('submitNewTask');
  const spinner = btn.querySelector('.spinner-border');
  btn.disabled = true;
  spinner.classList.remove('d-none');

  try {
    const payload = getTaskPayloadFromForm(form);
    await createTask(payload);

    // Cierra modal, limpia y notifica
    const modalEl = document.getElementById('createTaskModal');
    bootstrap.Modal.getOrCreateInstance(modalEl).hide();
    form.reset();
    form.classList.remove('was-validated');

    showToast('Task created successfully.', 'success', 1200);

    // Refresca todo (como pediste) después de un breve delay para que se vea el toast
    setTimeout(() => { location.reload(); }, 1300);

    // Alternativa sin recargar toda la página:
    // await loadTasks();
  } catch (err) {
    showToast(`Error creating task: ${err.message}`, 'danger', 2500);
  } finally {
    btn.disabled = false;
    spinner.classList.add('d-none');
  }
}

/* ========= Hook al cargar ========= */
document.addEventListener('DOMContentLoaded', () => {
  // ya llamas a loadTasks() aquí
  const form = document.getElementById('newTaskForm');
  if (form) form.addEventListener('submit', handleCreateTaskSubmit);
});
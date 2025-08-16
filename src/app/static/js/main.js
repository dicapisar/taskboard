/* ========= Config ========= */
const API_URL = '/api/v1/tasks/';

const statusToLabel = {
  not_started: 'Not Started',
  in_progress: 'In Progress',
  blocked: 'Blocked',
  completed: 'Completed',
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
  if (num === 1) return 'text-bg-primary';
  if (num === 2) return 'text-bg-warning';
  if (num === 3) return 'text-bg-danger';
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
  card.classList.toggle('opacity-50', isBusy);
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
    <a class="dropdown-item" href="#" data-details="true" data-task-id="${id}"><strong>Details</strong></a>
  `;
}

function setCardStatus(card, newStatus) {
  card.dataset.status = newStatus;
  refreshCardMenu(card);
}

/* ========= Persistencia (PATCH solo status) ========= */
async function updateTaskStatus(taskId, newStatus) {
  try {
    const resp = await fetch(`${API_URL}${taskId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ status: newStatus }),
    });

    let data = null;
    try { data = await resp.json(); } catch (_) {}

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
            <a class="dropdown-item" href="#" data-details="true" data-task-id="${id}">
              <strong>Details</strong>
            </a>
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
  document.querySelectorAll('.kanban-column').forEach(col => (col.innerHTML = ''));

  try {
    const resp = await fetch(API_URL, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
      credentials: 'include',
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

  targetCol.appendChild(card);
  setCardStatus(card, newStatus);

  await persistCardStatus(card, newStatus, oldStatus);
});

/* ========= Wrappers GLOBALS para handlers inline ========= */
window.allowDrop = function(event) {
  event.preventDefault();
};

window.drag = function(event) {
  event.dataTransfer.setData('text/html', event.currentTarget.outerHTML);
  event.dataTransfer.setData('text/plain', event.currentTarget.dataset.id);
  event.dataTransfer.setData('application/x-from-status', event.currentTarget.dataset.status || 'not_started');
};

window.drop = async function(event) {
  document.querySelectorAll('.kanban-column').forEach(column => column.classList.remove('drop'));
  event.preventDefault();

  const id = event.dataTransfer?.getData('text/plain');
  const html = event.dataTransfer?.getData('text/html');
  const fromStatus = event.dataTransfer?.getData('application/x-from-status') || 'not_started';
  if (!id || !html) return;

  try {
    const original = document.querySelector(`.kanban-card[data-id="${CSS.escape(id)}"]`);
    if (original) original.remove();
  } catch (e) {
    const original = document.querySelector(`.kanban-card[data-id="${id}"]`);
    if (original) original.remove();
  }

  event.currentTarget.insertAdjacentHTML('beforeend', html);

  let newCard;
  try {
    const list = event.currentTarget.querySelectorAll(`.kanban-card[data-id="${CSS.escape(id)}"]`);
    newCard = list[list.length - 1];
  } catch (e) {
    const list = event.currentTarget.querySelectorAll(`.kanban-card[data-id="${id}"]`);
    newCard = list[list.length - 1];
  }
  if (!newCard) return;

  newCard.setAttribute('draggable', 'true');
  newCard.setAttribute('ondragstart', 'drag(event)');

  const newStatus = getStatusByColumnEl(event.currentTarget);
  setCardStatus(newCard, newStatus);

  await persistCardStatus(newCard, newStatus, fromStatus);
};

/* ========= Crear tarea ========= */
function getTaskPayloadFromForm(form) {
  const status = form.status.value;
  return {
    title: (form.title.value || '').trim(),
    description: (form.description.value || '').trim(),
    completed: status === 'completed',
    priority: Number(form.priority.value),
    status,
    due_date: form.due_date.value,
    subject: (form.subject.value || '').trim(),
    created_at: new Date().toISOString().slice(0, 10),
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

/* ========= Submit del formulario (Create) ========= */
async function handleCreateTaskSubmit(ev) {
  ev.preventDefault();
  const form = ev.currentTarget;

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

    const modalEl = document.getElementById('createTaskModal');
    bootstrap.Modal.getOrCreateInstance(modalEl).hide();
    form.reset();
    form.classList.remove('was-validated');

    showToast('Task created successfully.', 'success', 1200);

    setTimeout(() => { location.reload(); }, 1300);
  } catch (err) {
    showToast(`Error creating task: ${err.message}`, 'danger', 2500);
  } finally {
    btn.disabled = false;
    spinner.classList.add('d-none');
  }
}

/* ========= API Details: obtener por id ========= */
async function getTaskById(taskId) {
  const resp = await fetch(`${API_URL}${taskId}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
    credentials: 'include'
  });

  let json = null;
  try { json = await resp.json(); } catch (_) {}

  if (!resp.ok) {
    const msg = json?.message || `HTTP ${resp.status}`;
    throw new Error(msg);
  }
  return json?.data;
}

/* ========= API Details: actualizar (POST con id en body) ========= */
async function updateTaskFull(payload) {
  const taskId = payload.id;
  const apiUrl = taskId ? `${API_URL}${taskId}` : API_URL; // si no hay id, es un nuevo POST

  const resp = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(payload)
  });

  let json = null;
  try { json = await resp.json(); } catch (_) {}

  if (!resp.ok) {
    const msg = json?.message || `HTTP ${resp.status}`;
    throw new Error(msg);
  }
  return json?.data ?? null;
}

/* ========= API Details: eliminar ========= */
async function deleteTask(taskId) {
  const resp = await fetch(`${API_URL}${taskId}`, {
    method: 'DELETE',
    headers: { 'Accept': 'application/json' },
    credentials: 'include'
  });

  let json = null;
  try { json = await resp.json(); } catch (_) {}

  if (!resp.ok) {
    const msg = json?.message || `HTTP ${resp.status}`;
    throw new Error(msg);
  }
  return json?.data ?? null;
}

/* ========= Helpers UI (Details/Delete) ========= */
function setDetailsFormBusy(isBusy) {
  const form = document.getElementById('taskDetailsForm');
  if (!form) return;

  [...form.elements].forEach(el => {
    if (el.id === 'submitUpdateTask') return;
    el.disabled = isBusy;
  });

  const btn = document.getElementById('submitUpdateTask');
  const spinner = btn?.querySelector('.spinner-border');
  if (btn) btn.disabled = isBusy;
  if (spinner) spinner.classList.toggle('d-none', !isBusy);

  // también bloquear el botón de eliminar mientras hay busy
  const delBtn = document.getElementById('openDeleteTask');
  if (delBtn) delBtn.disabled = isBusy || delBtn.dataset.ready !== '1';
}

function setConfirmDeleteBusy(isBusy) {
  const btn = document.getElementById('confirmDeleteBtn');
  if (!btn) return;
  const spinner = btn.querySelector('.spinner-border');
  btn.disabled = isBusy;
  if (spinner) spinner.classList.toggle('d-none', !isBusy);
}

function fillDetailsModal(task) {
  const form = document.getElementById('taskDetailsForm');
  if (!form) return;

  const idInput = form.elements['id'];
  if (idInput) idInput.value = task.id;

  form.title.value = task.title ?? '';
  form.description.value = task.description ?? '';
  form.priority.value = Number(task.priority ?? 2);
  form.status.value = task.status ?? (task.completed ? 'completed' : 'not_started');
  form.due_date.value = task.due_date ?? '';
  form.subject.value = task.subject ?? '';

  const createdAt = document.getElementById('detailCreatedAt');
  const owner = document.getElementById('detailOwner');
  if (createdAt) createdAt.value = task.created_at ?? '';
  if (owner) owner.value = (task.owner_id != null ? `#${task.owner_id}` : '');

  // habilitar el botón Delete y marcarlo como listo
  const delBtn = document.getElementById('openDeleteTask');
  if (delBtn) {
    delBtn.disabled = false;
    delBtn.dataset.ready = '1';
  }
}

function getTaskPayloadFromDetailsForm(form) {
  const idField = form.elements['id'];
  const status = form.status.value;
  return {
    id: idField ? Number(idField.value) : undefined,
    title: (form.title.value || '').trim(),
    description: (form.description.value || '').trim(),
    priority: Number(form.priority.value),
    status,
    due_date: form.due_date.value,
    subject: (form.subject.value || '').trim(),
  };
}

function removeTaskCardById(id) {
  try {
    const el = document.querySelector(`.kanban-card[data-id="${CSS.escape(String(id))}"]`);
    if (el) el.remove();
  } catch {
    const el = document.querySelector(`.kanban-card[data-id="${id}"]`);
    if (el) el.remove();
  }
}

function redrawTaskCard(task) {
  const id = task.id;
  const status = task.status || (task.completed ? 'completed' : 'not_started');
  const col = getColumnByStatus(status);
  if (!col) return;

  removeTaskCardById(id);
  col.insertAdjacentHTML('beforeend', createTaskHTML({ ...task, status }));
}

/* ========= Abrir modal Details ========= */
async function openTaskDetails(taskId) {
  const modalEl = document.getElementById('taskDetailsModal');
  const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

  const form = document.getElementById('taskDetailsForm');
  if (form) {
    form.reset();
    form.classList.remove('was-validated');
  }

  // deshabilitar temporalmente el botón Delete
  const delBtn = document.getElementById('openDeleteTask');
  if (delBtn) { delBtn.disabled = true; delBtn.dataset.ready = '0'; }

  modal.show();
  setDetailsFormBusy(true);

  try {
    const task = await getTaskById(taskId);
    fillDetailsModal(task);
  } catch (err) {
    showToast(`Error loading task #${taskId}: ${err.message}`, 'danger', 2500);
    modal.hide();
    return;
  } finally {
    setDetailsFormBusy(false);
  }
}

/* ========= Click en "Details" (delegación) ========= */
document.addEventListener('click', (ev) => {
  const link = ev.target.closest('a.dropdown-item[data-details="true"]');
  if (!link) return;
  ev.preventDefault();

  const taskId = link.dataset.taskId || link.closest('.kanban-card')?.dataset.id;
  if (!taskId) return;
  openTaskDetails(taskId);
});

/* ========= Eliminar: preparar confirmación ========= */
function prepConfirmDelete() {
  const form = document.getElementById('taskDetailsForm');
  if (!form) return;

  const idField = form.elements['id'];
  const id = idField ? Number(idField.value) : null;
  const title = form.title.value || '(no title)';

  const btn = document.getElementById('confirmDeleteBtn');
  const label = document.getElementById('confirmDeleteTaskTitle');
  if (btn) btn.dataset.taskId = String(id ?? '');
  if (label) label.textContent = `Task Title: ${title}`;
}

/* ========= Eliminar: ejecutar ========= */
async function executeDelete() {
  const btn = document.getElementById('confirmDeleteBtn');
  const taskId = btn?.dataset.taskId;
  if (!taskId) return;

  setConfirmDeleteBusy(true);
  try {
    await deleteTask(taskId);

    // Quitar tarjeta del tablero
    removeTaskCardById(taskId);

    // Cerrar ambos modales
    const confirmModalEl = document.getElementById('confirmDeleteModal');
    const detailsModalEl = document.getElementById('taskDetailsModal');
    bootstrap.Modal.getOrCreateInstance(confirmModalEl).hide();
    bootstrap.Modal.getOrCreateInstance(detailsModalEl).hide();

    showToast('Task deleted successfully.', 'success', 1500);
  } catch (err) {
    showToast(`Error deleting task: ${err.message}`, 'danger', 2500);
  } finally {
    setConfirmDeleteBusy(false);
  }
}

/* ========= Submit del formulario de Details ========= */
async function handleUpdateTaskSubmit(ev) {
  ev.preventDefault();
  const form = ev.currentTarget;

  if (!form.checkValidity()) {
    form.classList.add('was-validated');
    return;
  }

  setDetailsFormBusy(true);

  try {
    const payload = getTaskPayloadFromDetailsForm(form);
    if (!payload.id || Number.isNaN(payload.id)) {
      throw new Error('Invalid task id');
    }

    const apiReturnedTask = await updateTaskFull(payload);
    const latestTask = apiReturnedTask ?? (await getTaskById(payload.id));
    redrawTaskCard(latestTask);

    const modalEl = document.getElementById('taskDetailsModal');
    bootstrap.Modal.getOrCreateInstance(modalEl).hide();

    showToast('Task updated successfully.', 'success', 1200);
  } catch (err) {
    showToast(`Error updating task: ${err.message}`, 'danger', 2500);
  } finally {
    setDetailsFormBusy(false);
  }
}

/* ========= Hook al cargar ========= */
document.addEventListener('DOMContentLoaded', () => {
  loadTasks();

  const createForm = document.getElementById('newTaskForm');
  if (createForm) createForm.addEventListener('submit', handleCreateTaskSubmit);

  const detailsForm = document.getElementById('taskDetailsForm');
  if (detailsForm) detailsForm.addEventListener('submit', handleUpdateTaskSubmit);

  // Preparar datos al abrir el modal de confirmación
  const openDeleteBtn = document.getElementById('openDeleteTask');
  if (openDeleteBtn) openDeleteBtn.addEventListener('click', prepConfirmDelete);

  // Ejecutar la eliminación
  const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
  if (confirmDeleteBtn) confirmDeleteBtn.addEventListener('click', executeDelete);
});
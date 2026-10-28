let currentProcesses = [];
let currentResources = [];
let activeProcessId = null;

async function loadProcesses() {
  try {
    const [pRes, rRes] = await Promise.all([
      fetch('/api/processes').then(r => r.json()),
      fetch('/api/resources').then(r => r.json())
    ]);

    currentProcesses = pRes;
    currentResources = rRes;

    const tbody = document.getElementById('processes-table-body');
    if (!pRes || pRes.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-4">No processes created yet.</td></tr>';
      return;
    }

    tbody.innerHTML = pRes.map(p => {
      let badgeClass = 'badge-ready';
      if (p.state === 'RUNNING') badgeClass = 'badge-running';
      else if (p.state === 'DEADLOCKED') badgeClass = 'badge-deadlocked';
      else if (p.state === 'WAITING') badgeClass = 'badge-waiting';
      else if (p.state === 'BLOCKED') badgeClass = 'badge-blocked';
      else if (p.state === 'COMPLETED') badgeClass = 'badge-completed';
      else if (p.state === 'TERMINATED') badgeClass = 'badge-terminated';

      const allocStr = Object.entries(p.allocation || {}).map(([r, v]) => `${r}: ${v}`).join(', ') || '0';
      const maxStr = Object.entries(p.maximum || {}).map(([r, v]) => `${r}: ${v}`).join(', ') || '0';
      const needStr = Object.entries(p.need || {}).map(([r, v]) => `${r}: ${v}`).join(', ') || '0';

      const pendingReqStr = p.pending_request 
        ? `<span class="badge bg-warning text-dark">${Object.entries(p.pending_request).map(([r, v]) => `${r}:${v}`).join(', ')}</span>` 
        : '<span class="text-muted small">None</span>';

      const isInactive = (p.state === 'TERMINATED' || p.state === 'COMPLETED');

      return `
        <tr>
          <td><strong class="font-monospace">${p.pid}</strong></td>
          <td>${p.name}</td>
          <td><span class="badge-status ${badgeClass}">${p.state}</span></td>
          <td><code>[${allocStr}]</code></td>
          <td><code>[${maxStr}]</code></td>
          <td><code>[${needStr}]</code></td>
          <td>${pendingReqStr}</td>
          <td class="text-end">
            <div class="btn-group btn-group-sm">
              <button class="btn btn-outline-primary" ${isInactive ? 'disabled' : ''} onclick="openRequestModal(${p.id})" title="Request Resources">
                <i class="bi bi-send"></i> Req
              </button>
              <button class="btn btn-outline-success" ${isInactive ? 'disabled' : ''} onclick="openReleaseModal(${p.id})" title="Release Resources">
                <i class="bi bi-box-arrow-right"></i> Rel
              </button>
              <button class="btn btn-outline-secondary" ${isInactive ? 'disabled' : ''} onclick="completeProcess(${p.id})" title="Complete Process">
                <i class="bi bi-check2-circle"></i>
              </button>
              <button class="btn btn-outline-danger" ${isInactive ? 'disabled' : ''} onclick="terminateProcess(${p.id})" title="Terminate Process">
                <i class="bi bi-stop-circle"></i>
              </button>
              <button class="btn btn-outline-dark" onclick="deleteProcess(${p.id})" title="Delete Process">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    showToast('Failed to load processes: ' + err, 'error');
  }
}

async function prepareCreateModal() {
  const container = document.getElementById('new-proc-resource-inputs');
  if (currentResources.length === 0) {
    container.innerHTML = '<div class="alert alert-warning">No resources exist in the system. Please create resources first on the Resources page.</div>';
    return;
  }

  container.innerHTML = `
    <div class="table-responsive">
      <table class="table table-bordered table-sm align-middle">
        <thead class="table-light">
          <tr>
            <th>Resource</th>
            <th>System Available / Total</th>
            <th>Maximum Demand (Max)</th>
            <th>Initial Allocation</th>
          </tr>
        </thead>
        <tbody>
          ${currentResources.map(r => `
            <tr>
              <td><strong>${r.name} (${r.resource_id})</strong></td>
              <td>${r.available_instances} / ${r.total_instances}</td>
              <td><input type="number" min="0" max="${r.total_instances}" class="form-control form-control-sm new-proc-max" data-rid="${r.resource_id}" value="0"></td>
              <td><input type="number" min="0" max="${r.available_instances}" class="form-control form-control-sm new-proc-alloc" data-rid="${r.resource_id}" value="0"></td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

async function submitCreateProcess() {
  const pid = document.getElementById('new-pid').value.trim();
  const name = document.getElementById('new-pname').value.trim();

  if (!pid || !name) {
    showToast('Please provide both PID and Name.', 'error');
    return;
  }

  const maximums = {};
  const allocations = {};

  document.querySelectorAll('.new-proc-max').forEach(inp => {
    maximums[inp.dataset.rid] = parseInt(inp.value) || 0;
  });

  document.querySelectorAll('.new-proc-alloc').forEach(inp => {
    allocations[inp.dataset.rid] = parseInt(inp.value) || 0;
  });

  try {
    const res = await fetch('/api/processes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pid, name, maximum: maximums, allocation: allocations })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Process created.', 'success');
      bootstrap.Modal.getInstance(document.getElementById('createProcessModal')).hide();
      document.getElementById('createProcessForm').reset();
      loadProcesses();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to create process.', 'error');
    }
  } catch (err) {
    showToast('Request error: ' + err, 'error');
  }
}

function openRequestModal(procId) {
  const proc = currentProcesses.find(p => p.id === procId);
  if (!proc) return;
  activeProcessId = procId;

  document.getElementById('req-modal-pid').innerText = `${proc.name} (${proc.pid})`;
  const container = document.getElementById('request-vector-inputs');

  container.innerHTML = `
    <table class="table table-sm table-bordered">
      <thead class="table-light">
        <tr>
          <th>Resource</th>
          <th>Available</th>
          <th>Remaining Need</th>
          <th>Request Quantity</th>
        </tr>
      </thead>
      <tbody>
        ${currentResources.map(r => {
          const avail = r.available_instances;
          const need = (proc.need && proc.need[r.resource_id]) || 0;
          return `
            <tr>
              <td><strong>${r.name} (${r.resource_id})</strong></td>
              <td>${avail}</td>
              <td>${need}</td>
              <td>
                <input type="number" min="0" max="${need}" class="form-control form-control-sm proc-req-input" data-rid="${r.resource_id}" value="0">
              </td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;

  const modal = new bootstrap.Modal(document.getElementById('requestModal'));
  modal.show();
}

async function submitResourceRequest() {
  const proc = currentProcesses.find(p => p.id === activeProcessId);
  if (!proc) return;

  const requestVector = {};
  document.querySelectorAll('.proc-req-input').forEach(inp => {
    requestVector[inp.dataset.rid] = parseInt(inp.value) || 0;
  });

  try {
    const res = await fetch('/api/resource-request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pid: proc.pid, request: requestVector })
    });
    const data = await res.json();
    if (res.ok) {
      if (data.granted) {
        showToast(`Request GRANTED! Safe sequence: ${data.safe_sequence ? data.safe_sequence.join(' → ') : 'Safe'}`, 'success');
      } else {
        showToast(`Request DENIED: ${data.reason}`, 'warning');
      }
      bootstrap.Modal.getInstance(document.getElementById('requestModal')).hide();
      loadProcesses();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to submit request.', 'error');
    }
  } catch (err) {
    showToast('Error submitting request: ' + err, 'error');
  }
}

function openReleaseModal(procId) {
  const proc = currentProcesses.find(p => p.id === procId);
  if (!proc) return;
  activeProcessId = procId;

  document.getElementById('rel-modal-pid').innerText = `${proc.name} (${proc.pid})`;
  const container = document.getElementById('release-vector-inputs');

  container.innerHTML = `
    <table class="table table-sm table-bordered">
      <thead class="table-light">
        <tr>
          <th>Resource</th>
          <th>Currently Allocated</th>
          <th>Release Quantity</th>
        </tr>
      </thead>
      <tbody>
        ${currentResources.map(r => {
          const held = (proc.allocation && proc.allocation[r.resource_id]) || 0;
          return `
            <tr>
              <td><strong>${r.name} (${r.resource_id})</strong></td>
              <td>${held}</td>
              <td>
                <input type="number" min="0" max="${held}" class="form-control form-control-sm proc-rel-input" data-rid="${r.resource_id}" value="0">
              </td>
            </tr>
          `;
        }).join('')}
      </tbody>
    </table>
  `;

  const modal = new bootstrap.Modal(document.getElementById('releaseModal'));
  modal.show();
}

async function submitResourceRelease() {
  const releaseVector = {};
  document.querySelectorAll('.proc-rel-input').forEach(inp => {
    const qty = parseInt(inp.value) || 0;
    if (qty > 0) releaseVector[inp.dataset.rid] = qty;
  });

  try {
    const res = await fetch(`/api/processes/${activeProcessId}/release`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ release: releaseVector })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Resources released.', 'success');
      bootstrap.Modal.getInstance(document.getElementById('releaseModal')).hide();
      loadProcesses();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to release resources.', 'error');
    }
  } catch (err) {
    showToast('Error releasing resources: ' + err, 'error');
  }
}

async function completeProcess(procId) {
  if (!confirm('Mark process as completed and release all its held resources?')) return;
  try {
    const res = await fetch(`/api/processes/${procId}/complete`, { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'Process completed.', 'success');
    loadProcesses();
    updateGlobalStatus();
  } catch (err) {
    showToast('Failed to complete process: ' + err, 'error');
  }
}

async function terminateProcess(procId) {
  if (!confirm('Force terminate process? All held resources will be immediately reclaimed.')) return;
  try {
    const res = await fetch(`/api/processes/${procId}/terminate`, { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'Process terminated.', 'warning');
    loadProcesses();
    updateGlobalStatus();
  } catch (err) {
    showToast('Failed to terminate process: ' + err, 'error');
  }
}

async function deleteProcess(procId) {
  if (!confirm('Delete process permanently?')) return;
  try {
    const res = await fetch(`/api/processes/${procId}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Process deleted.', 'success');
      loadProcesses();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to delete process.', 'error');
    }
  } catch (err) {
    showToast('Failed to delete process: ' + err, 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadProcesses);

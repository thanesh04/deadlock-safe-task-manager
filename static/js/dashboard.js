let stateChart = null;
let resourceChart = null;

async function loadDashboardData() {
  try {
    const [procRes, resRes, safetyRes, deadlockRes, logsRes] = await Promise.all([
      fetch('/api/processes').then(r => r.json()),
      fetch('/api/resources').then(r => r.json()),
      fetch('/api/safety-check').then(r => r.json()),
      fetch('/api/deadlock-detection').then(r => r.json()),
      fetch('/api/logs?limit=5').then(r => r.json())
    ]);

    // Safety Card
    const safetyStatus = document.getElementById('dash-safety-status');
    const safetySub = document.getElementById('dash-safety-sub');
    if (safetyRes.safe) {
      safetyStatus.innerHTML = '<span class="text-success"><i class="bi bi-shield-check"></i> SAFE</span>';
      safetySub.innerText = `Sequence: ${safetyRes.safe_sequence.join(' → ')}`;
    } else {
      safetyStatus.innerHTML = '<span class="text-warning"><i class="bi bi-exclamation-triangle-fill"></i> UNSAFE</span>';
      safetySub.innerText = `Unfinished: ${(safetyRes.unfinished_processes || []).join(', ') || 'No safe sequence'}`;
    }

    // Deadlock Card
    const deadlockStatus = document.getElementById('dash-deadlock-status');
    const deadlockSub = document.getElementById('dash-deadlock-sub');
    if (deadlockRes.deadlock) {
      deadlockStatus.innerHTML = '<span class="text-danger"><i class="bi bi-x-octagon-fill"></i> DEADLOCK</span>';
      deadlockSub.innerText = `Deadlocked: ${deadlockRes.deadlocked_processes.join(', ')}`;
    } else {
      deadlockStatus.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill"></i> NONE</span>';
      deadlockSub.innerText = 'No deadlock detected';
    }

    // Process Counts
    document.getElementById('dash-proc-count').innerText = procRes.length;
    const states = { RUNNING: 0, WAITING: 0, BLOCKED: 0, READY: 0, DEADLOCKED: 0, COMPLETED: 0, TERMINATED: 0 };
    procRes.forEach(p => {
      states[p.state] = (states[p.state] || 0) + 1;
    });

    document.getElementById('cnt-running').innerText = states.RUNNING || 0;
    document.getElementById('cnt-waiting').innerText = (states.WAITING || 0) + (states.BLOCKED || 0);
    document.getElementById('cnt-deadlocked').innerText = states.DEADLOCKED || 0;
    document.getElementById('cnt-completed').innerText = states.COMPLETED || 0;
    document.getElementById('dash-proc-breakdown').innerText = `${states.RUNNING || 0} Running, ${(states.WAITING || 0) + (states.BLOCKED || 0)} Waiting`;

    // Resource Counts
    document.getElementById('dash-res-count').innerText = resRes.length;
    const totalAvail = resRes.reduce((acc, r) => acc + r.available_instances, 0);
    const totalCap = resRes.reduce((acc, r) => acc + r.total_instances, 0);
    document.getElementById('dash-res-avail').innerText = `${totalAvail} / ${totalCap} available instances`;

    // Process Table
    renderProcessTable(procRes);

    // Charts
    renderCharts(states, resRes);

    // Recent Logs
    renderRecentLogs(logsRes);

  } catch (err) {
    console.error("Error loading dashboard data:", err);
  }
}

function renderProcessTable(processes) {
  const tbody = document.getElementById('dash-proc-table');
  if (!processes || processes.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-3">No active processes found. Click "Add Process" or load a scenario.</td></tr>';
    return;
  }

  tbody.innerHTML = processes.map(p => {
    let badgeClass = 'badge-ready';
    if (p.state === 'RUNNING') badgeClass = 'badge-running';
    else if (p.state === 'DEADLOCKED') badgeClass = 'badge-deadlocked';
    else if (p.state === 'WAITING') badgeClass = 'badge-waiting';
    else if (p.state === 'BLOCKED') badgeClass = 'badge-blocked';
    else if (p.state === 'COMPLETED') badgeClass = 'badge-completed';
    else if (p.state === 'TERMINATED') badgeClass = 'badge-terminated';

    const allocStr = Object.entries(p.allocation || {}).map(([r, v]) => `${r}:${v}`).join(', ') || 'None';
    const maxStr = Object.entries(p.maximum || {}).map(([r, v]) => `${r}:${v}`).join(', ') || 'None';

    return `
      <tr>
        <td><strong>${p.pid}</strong></td>
        <td>${p.name}</td>
        <td><span class="badge-status ${badgeClass}">${p.state}</span></td>
        <td><code>[${allocStr}]</code></td>
        <td><code>[${maxStr}]</code></td>
        <td>
          <button class="btn btn-sm btn-outline-danger" title="Terminate Process" onclick="terminateProc(${p.id})">
            <i class="bi bi-x-circle"></i>
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function renderCharts(states, resources) {
  // 1. Process State Doughnut
  const ctxState = document.getElementById('procStateChart').getContext('2d');
  if (stateChart) stateChart.destroy();

  stateChart = new Chart(ctxState, {
    type: 'doughnut',
    data: {
      labels: ['Running', 'Waiting/Blocked', 'Deadlocked', 'Ready', 'Completed'],
      datasets: [{
        data: [
          states.RUNNING || 0,
          (states.WAITING || 0) + (states.BLOCKED || 0),
          states.DEADLOCKED || 0,
          states.READY || 0,
          states.COMPLETED || 0
        ],
        backgroundColor: ['#2563eb', '#f59e0b', '#ef4444', '#94a3b8', '#10b981'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12 } }
      }
    }
  });

  // 2. Resource Stacked Bar
  const ctxRes = document.getElementById('resourceUtilChart').getContext('2d');
  if (resourceChart) resourceChart.destroy();

  const labels = resources.map(r => `${r.name} (${r.resource_id})`);
  const allocatedData = resources.map(r => r.allocated_instances);
  const availableData = resources.map(r => r.available_instances);

  resourceChart = new Chart(ctxRes, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        { label: 'Allocated', data: allocatedData, backgroundColor: '#3b82f6' },
        { label: 'Available', data: availableData, backgroundColor: '#10b981' }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true }
      },
      plugins: {
        legend: { position: 'bottom', labels: { boxWidth: 12 } }
      }
    }
  });
}

function renderRecentLogs(logs) {
  const container = document.getElementById('dash-recent-logs');
  if (!logs || logs.length === 0) {
    container.innerHTML = 'No recent activity.';
    return;
  }

  container.innerHTML = logs.map(l => `
    <div class="mb-2 pb-2 border-bottom">
      <div class="d-flex justify-content-between text-muted" style="font-size: 0.72rem;">
        <span class="fw-semibold text-dark">${l.event_type}</span>
        <span>${l.timestamp ? l.timestamp.split(' ')[1] : ''}</span>
      </div>
      <div class="text-truncate text-secondary" style="font-size: 0.8rem;" title="${l.description}">
        ${l.description}
      </div>
    </div>
  `).join('');
}

async function terminateProc(procId) {
  if (!confirm('Terminate this process and release all its allocated resources?')) return;
  try {
    const res = await fetch(`/api/processes/${procId}/terminate`, { method: 'POST' });
    const data = await res.json();
    showToast(data.message || 'Process terminated', 'success');
    loadDashboardData();
    updateGlobalStatus();
  } catch (err) {
    showToast('Failed to terminate process: ' + err, 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadDashboardData);

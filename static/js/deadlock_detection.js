let lastDetectionData = null;

async function runDetection() {
  const btn = document.getElementById('btn-run-detection');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Checking Deadlocks...';

  try {
    const res = await fetch('/api/deadlock-detection', { method: 'POST' });
    const data = await res.json();
    lastDetectionData = data;

    const banner = document.getElementById('detection-result-banner');
    const bannerCard = document.getElementById('detection-banner-card');
    const bannerTitle = document.getElementById('detection-banner-title');
    const bannerSub = document.getElementById('detection-banner-sub');
    const bannerIcon = document.getElementById('detection-banner-icon');
    const recoveryPanel = document.getElementById('recovery-panel');

    banner.classList.remove('d-none');

    if (data.deadlock) {
      bannerCard.className = 'card p-3 shadow-sm border-0 bg-danger-subtle text-danger';
      bannerTitle.innerHTML = '<i class="bi bi-x-octagon-fill me-2"></i>DEADLOCK DETECTED!';
      bannerSub.innerHTML = `Deadlocked Processes: <strong class="text-dark">${data.deadlocked_processes.join(', ')}</strong>`;
      bannerIcon.innerHTML = '<i class="bi bi-exclamation-octagon-fill text-danger"></i>';
      recoveryPanel.classList.remove('d-none');
      populateRecoveryOptions(data.deadlocked_processes);
      showToast('Deadlock detected in current state!', 'error');
    } else {
      bannerCard.className = 'card p-3 shadow-sm border-0 bg-success-subtle text-success';
      bannerTitle.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>NO DEADLOCK';
      bannerSub.innerHTML = `All active processes can eventually be satisfied. Execution order: <strong class="text-dark">${data.satisfied_processes.join(' &rarr; ') || 'All clear'}</strong>`;
      bannerIcon.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
      recoveryPanel.classList.add('d-none');
      showToast('No deadlock detected.', 'success');
    }

    renderDetectionTrace(data.steps || []);
    renderFinishVector(data.finish || {}, data.work_final || {});
    document.getElementById('detection-step-count').innerText = `${(data.steps || []).length} Steps Recorded`;
    updateGlobalStatus();

  } catch (err) {
    showToast('Deadlock detection failed: ' + err, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-search me-1"></i> RUN DEADLOCK DETECTION';
  }
}

function renderDetectionTrace(steps) {
  const container = document.getElementById('detection-trace-container');
  if (!steps || steps.length === 0) {
    container.innerHTML = '<div class="alert alert-info">No processes found in simulation.</div>';
    return;
  }

  container.innerHTML = steps.map(s => {
    let badgeClass = 'bg-secondary';
    if (s.action === 'INITIALIZATION') badgeClass = 'bg-info text-dark';
    else if (s.action === 'SATISFY_REQUEST') badgeClass = 'bg-success';
    else if (s.action === 'DEADLOCKED') badgeClass = 'bg-danger';

    const workStr = s.work_after 
      ? Object.entries(s.work_after).map(([r, v]) => `${r}:${v}`).join(', ')
      : (s.work ? Object.entries(s.work).map(([r, v]) => `${r}:${v}`).join(', ') : '');

    const reqStr = s.request ? Object.entries(s.request).map(([r, v]) => `${r}:${v}`).join(', ') : '';

    return `
      <div class="step-item">
        <div class="step-badge">${s.step}</div>
        <div class="card p-3 border mb-3">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <h6 class="fw-bold mb-0">Action: ${s.action} - <span class="badge bg-light text-dark border">${s.process}</span></h6>
            <span class="badge ${badgeClass}">${s.decision}</span>
          </div>
          <div class="small text-muted mb-2">${s.explanation}</div>
          <div class="row g-2 small">
            ${reqStr ? `<div class="col-6"><strong>Request:</strong> <code>[${reqStr}]</code></div>` : ''}
            ${workStr ? `<div class="col-6"><strong>Work:</strong> <code>[${workStr}]</code></div>` : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function renderFinishVector(finish, workFinal) {
  const container = document.getElementById('finish-vector-display');
  const finishItems = Object.entries(finish).map(([p, done]) => `
    <li class="list-group-item d-flex justify-content-between align-items-center py-1">
      <span class="font-monospace fw-semibold">${p}</span>
      <span class="badge ${done ? 'bg-success' : 'bg-danger'}">${done ? 'true' : 'false (DEADLOCKED)'}</span>
    </li>
  `).join('');

  const workItems = Object.entries(workFinal).map(([r, val]) => `
    <span class="badge bg-light text-dark border p-2">
      <span class="text-muted">${r}:</span> <strong class="text-success">${val}</strong>
    </span>
  `).join('');

  container.innerHTML = `
    <div class="mb-3">
      <label class="fw-semibold small d-block mb-1">Finish Vector [Finish]:</label>
      <ul class="list-group list-group-flush border rounded small">
        ${finishItems}
      </ul>
    </div>
    <div>
      <label class="fw-semibold small d-block mb-1">Final Work Vector:</label>
      <div class="d-flex flex-wrap gap-1">
        ${workItems}
      </div>
    </div>
  `;
}

function populateRecoveryOptions(deadlockedPids) {
  const victimSelect = document.getElementById('terminate-victim-select');
  victimSelect.innerHTML = deadlockedPids.map(p => `<option value="${p}">${p}</option>`).join('');

  const preemptVictim = document.getElementById('preempt-victim-select');
  const preemptTarget = document.getElementById('preempt-target-select');
  const preemptRes = document.getElementById('preempt-resource-select');

  preemptVictim.innerHTML = deadlockedPids.map(p => `<option value="${p}">${p}</option>`).join('');
  preemptTarget.innerHTML = deadlockedPids.map(p => `<option value="${p}">${p}</option>`).join('');

  if (lastDetectionData && lastDetectionData.matrices && lastDetectionData.matrices.resources) {
    preemptRes.innerHTML = lastDetectionData.matrices.resources.map(r => `<option value="${r}">${r}</option>`).join('');
  }
}

async function terminateVictim() {
  const pid = document.getElementById('terminate-victim-select').value;
  if (!pid) return;

  if (!confirm(`Terminate process ${pid} to recover from deadlock?`)) return;

  try {
    const res = await fetch('/api/recovery', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_type: 'terminate', params: { pids: [pid] } })
    });
    const data = await res.json();
    if (data.deadlock_resolved) {
      showToast(`Recovery Successful! Process ${pid} terminated and deadlock is RESOLVED!`, 'success');
    } else {
      showToast(`Process ${pid} terminated. Deadlock persists with: ${data.remaining_deadlocked.join(', ')}`, 'warning');
    }
    // Re-run detection to refresh view
    setTimeout(runDetection, 600);
  } catch (err) {
    showToast('Recovery failed: ' + err, 'error');
  }
}

async function terminateAllDeadlocked() {
  if (!lastDetectionData || !lastDetectionData.deadlocked_processes) return;
  const pids = lastDetectionData.deadlocked_processes;
  if (!confirm(`Terminate all deadlocked processes (${pids.join(', ')})?`)) return;

  try {
    const res = await fetch('/api/recovery', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_type: 'terminate', params: { pids } })
    });
    const data = await res.json();
    showToast('All deadlocked processes terminated. Deadlock resolved!', 'success');
    setTimeout(runDetection, 600);
  } catch (err) {
    showToast('Recovery failed: ' + err, 'error');
  }
}

async function simulatePreemption() {
  const victim = document.getElementById('preempt-victim-select').value;
  const target = document.getElementById('preempt-target-select').value;
  const resource = document.getElementById('preempt-resource-select').value;

  if (victim === target) {
    showToast('Victim and target process must be different.', 'warning');
    return;
  }

  try {
    const res = await fetch('/api/recovery', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action_type: 'preempt',
        params: { victim_pid: victim, target_pid: target, resource_id: resource, quantity: 1 }
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, data.deadlock_resolved ? 'success' : 'info');
      // Re-run detection to display updated state
      setTimeout(runDetection, 600);
    } else {
      showToast(data.message || 'Preemption failed.', 'error');
    }
  } catch (err) {
    showToast('Preemption simulation failed: ' + err, 'error');
  }
}

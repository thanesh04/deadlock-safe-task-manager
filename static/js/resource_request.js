let reqProcesses = [];
let reqResources = [];
let matrixData = {};

async function loadRequestPage() {
  try {
    const res = await fetch('/api/matrices');
    matrixData = await res.json();
    reqProcesses = matrixData.processes || [];
    reqResources = matrixData.resources || [];

    const select = document.getElementById('req-process-select');
    select.innerHTML = '<option value="">-- Select Process --</option>' + 
      reqProcesses.map(p => `<option value="${p}">${p}</option>`).join('');

  } catch (err) {
    showToast('Failed to load matrix context: ' + err, 'error');
  }
}

function updateProcessContext() {
  const select = document.getElementById('req-process-select');
  const pid = select.value;
  const contextBox = document.getElementById('proc-context-box');
  const inputContainer = document.getElementById('req-vector-inputs');

  if (!pid) {
    contextBox.classList.add('d-none');
    inputContainer.innerHTML = '<span class="text-muted small">Select a process to configure resource inputs.</span>';
    return;
  }

  contextBox.classList.remove('d-none');
  const alloc = matrixData.allocation[pid] || {};
  const max = matrixData.maximum[pid] || {};
  const need = matrixData.need[pid] || {};

  document.getElementById('proc-context-alloc').innerText = `[${reqResources.map(r => `${r}:${alloc[r] || 0}`).join(', ')}]`;
  document.getElementById('proc-context-max').innerText = `[${reqResources.map(r => `${r}:${max[r] || 0}`).join(', ')}]`;
  document.getElementById('proc-context-need').innerText = `[${reqResources.map(r => `${r}:${need[r] || 0}`).join(', ')}]`;

  inputContainer.innerHTML = `
    <div class="row g-2">
      ${reqResources.map(r => {
        const remNeed = need[r] || 0;
        const avail = matrixData.available[r] || 0;
        return `
          <div class="col-6">
            <label class="form-label small fw-semibold mb-1">${r} (Need: ${remNeed}, Avail: ${avail})</label>
            <input type="number" min="0" max="${remNeed}" class="form-control form-control-sm req-field" data-rid="${r}" value="0">
          </div>
        `;
      }).join('')}
    </div>
  `;
}

async function submitRequestAlgorithm() {
  const select = document.getElementById('req-process-select');
  const pid = select.value;

  if (!pid) {
    showToast('Please select a process first.', 'warning');
    return;
  }

  const requestVector = {};
  document.querySelectorAll('.req-field').forEach(inp => {
    requestVector[inp.dataset.rid] = parseInt(inp.value) || 0;
  });

  const btn = document.getElementById('btn-submit-request');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Testing Request...';

  try {
    const res = await fetch('/api/resource-request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pid, request: requestVector })
    });
    const data = await res.json();

    const decisionBadge = document.getElementById('request-decision-badge');
    if (data.granted) {
      decisionBadge.className = 'badge bg-success fs-6';
      decisionBadge.innerHTML = '<i class="bi bi-check-circle me-1"></i> REQUEST GRANTED';
      showToast('Request granted and committed to state!', 'success');
    } else {
      decisionBadge.className = 'badge bg-danger fs-6';
      decisionBadge.innerHTML = '<i class="bi bi-x-circle me-1"></i> REQUEST DENIED';
      showToast(data.reason || 'Request denied.', 'error');
    }

    renderStepper(data, pid, requestVector);
    updateGlobalStatus();

    // Reload matrices for updated state
    const reloadRes = await fetch('/api/matrices');
    matrixData = await reloadRes.json();
    updateProcessContext();

  } catch (err) {
    showToast('Request processing failed: ' + err, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-arrow-right-circle me-1"></i> Evaluate & Allocate Request';
  }
}

function renderStepper(data, pid, reqVector) {
  const container = document.getElementById('request-stepper-container');
  const reqStr = Object.entries(reqVector).map(([r, v]) => `${r}:${v}`).join(', ');
  const steps = data.steps_log || [];

  container.innerHTML = `
    <div class="alert alert-light border mb-4">
      <div class="fw-bold">Evaluating: Process <code>${pid}</code> requests <code>[${reqStr}]</code></div>
      <div class="small text-muted mt-1">${data.reason}</div>
    </div>

    <!-- Step 1 -->
    <div class="step-item">
      <div class="step-badge">${data.step_failed === 1 ? '<i class="bi bi-x"></i>' : '1'}</div>
      <div class="card p-3 border mb-3">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <h6 class="fw-bold mb-0">Step 1: Request &le; Need Condition</h6>
          <span class="badge ${data.step_failed === 1 ? 'bg-danger' : 'bg-success'}">
            ${data.step_failed === 1 ? 'VIOLATED' : 'PASSED'}
          </span>
        </div>
        <p class="small text-muted mb-0">
          Does the process request exceed its initially declared maximum claim?
          ${data.step_failed === 1 ? `<br><strong class="text-danger">${data.reason}</strong>` : ' Request is within the process claim boundaries.'}
        </p>
      </div>
    </div>

    <!-- Step 2 -->
    <div class="step-item">
      <div class="step-badge">${data.step_failed === 2 ? '<i class="bi bi-x"></i>' : '2'}</div>
      <div class="card p-3 border mb-3">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <h6 class="fw-bold mb-0">Step 2: Request &le; Available Condition</h6>
          <span class="badge ${data.step_failed === 2 ? 'bg-danger' : (data.step_failed === 1 ? 'bg-secondary' : 'bg-success')}">
            ${data.step_failed === 2 ? 'INSUFFICIENT' : (data.step_failed === 1 ? 'SKIPPED' : 'PASSED')}
          </span>
        </div>
        <p class="small text-muted mb-0">
          Are sufficient instances currently free in the system available pool?
          ${data.step_failed === 2 ? `<br><strong class="text-danger">${data.reason}</strong>` : (data.step_failed === 1 ? ' Skipped due to previous step failure.' : ' System has sufficient available resources.')}
        </p>
      </div>
    </div>

    <!-- Step 3 -->
    <div class="step-item">
      <div class="step-badge">3</div>
      <div class="card p-3 border mb-3">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <h6 class="fw-bold mb-0">Step 3: Tentative State Simulation</h6>
          <span class="badge ${data.step_failed && data.step_failed < 3 ? 'bg-secondary' : 'bg-info'}">
            ${data.step_failed && data.step_failed < 3 ? 'SKIPPED' : 'SIMULATED'}
          </span>
        </div>
        <p class="small text-muted mb-1">
          The OS pretends to allocate the requested resources:
          <code>Available' = Available - Request</code>, 
          <code>Alloc[${pid}]' = Alloc[${pid}] + Request</code>, 
          <code>Need[${pid}]' = Need[${pid}] - Request</code>.
        </p>
      </div>
    </div>

    <!-- Step 4 -->
    <div class="step-item">
      <div class="step-badge">${data.step_failed === 4 ? '<i class="bi bi-x"></i>' : '4'}</div>
      <div class="card p-3 border mb-3">
        <div class="d-flex justify-content-between align-items-center mb-1">
          <h6 class="fw-bold mb-0">Step 4: Safety Algorithm Verification</h6>
          <span class="badge ${data.step_failed === 4 ? 'bg-danger' : (data.granted ? 'bg-success' : 'bg-secondary')}">
            ${data.step_failed === 4 ? 'UNSAFE' : (data.granted ? 'SAFE' : 'NOT TESTED')}
          </span>
        </div>
        <p class="small text-muted mb-0">
          Runs Banker's Safety Algorithm on the tentative state to ensure deadlock avoidance.
          ${data.granted ? `<br><span class="text-success fw-bold">Safe sequence found: ${data.safe_sequence ? data.safe_sequence.join(' &rarr; ') : 'Safe'}</span>` : ''}
          ${data.step_failed === 4 ? '<br><span class="text-danger fw-bold">Tentative state is UNSAFE. Allocation rolled back.</span>' : ''}
        </p>
      </div>
    </div>

    <!-- Step 5 -->
    <div class="step-item">
      <div class="step-badge">${data.granted ? '<i class="bi bi-check"></i>' : '<i class="bi bi-x"></i>'}</div>
      <div class="card p-3 border ${data.granted ? 'border-success' : 'border-danger'}">
        <h6 class="fw-bold ${data.granted ? 'text-success' : 'text-danger'} mb-1">Step 5: Final Decision</h6>
        <div class="small fw-semibold">
          ${data.granted ? 'REQUEST GRANTED: Tentative allocation committed to actual database state.' : 'REQUEST DENIED: State restored to previous safe condition.'}
        </div>
      </div>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', loadRequestPage);

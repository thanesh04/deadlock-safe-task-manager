async function loadSafetyInit() {
  try {
    const res = await fetch('/api/matrices');
    const data = await res.json();
    const container = document.getElementById('safety-available-summary');

    if (data.resources && data.resources.length > 0) {
      container.innerHTML = `
        <div class="d-flex flex-wrap gap-2">
          ${data.resources.map(r => `
            <div class="badge bg-light text-dark border p-2">
              <span class="text-muted">${r}:</span> <strong class="text-success">${data.available[r] ?? 0}</strong>
            </div>
          `).join('')}
        </div>
      `;
    } else {
      container.innerText = 'No resources found.';
    }
  } catch (e) {
    console.error('Init error', e);
  }
}

async function runSafetyAnalysis() {
  const btn = document.getElementById('btn-run-safety');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Evaluating...';

  try {
    const res = await fetch('/api/safety-check', { method: 'POST' });
    const data = await res.json();

    const banner = document.getElementById('safety-result-banner');
    const bannerCard = document.getElementById('safety-banner-card');
    const bannerTitle = document.getElementById('safety-banner-title');
    const bannerSeq = document.getElementById('safety-banner-sequence');
    const bannerIcon = document.getElementById('safety-banner-icon');

    banner.classList.remove('d-none');

    if (data.safe) {
      bannerCard.className = 'card p-3 shadow-sm border-0 bg-success-subtle text-success';
      bannerTitle.innerHTML = '<i class="bi bi-shield-check me-2"></i>SAFE STATE';
      bannerSeq.innerHTML = `Safe Execution Sequence: <strong class="text-dark">${data.safe_sequence.join(' &rarr; ')}</strong>`;
      bannerIcon.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i>';
      showToast('System is in a SAFE state!', 'success');
    } else {
      bannerCard.className = 'card p-3 shadow-sm border-0 bg-danger-subtle text-danger';
      bannerTitle.innerHTML = '<i class="bi bi-shield-x me-2"></i>UNSAFE STATE';
      const unfin = (data.unfinished_processes || []).join(', ') || 'Processes blocked';
      bannerSeq.innerHTML = `No safe sequence exists. Unfinished processes: <strong class="text-dark">${unfin}</strong>`;
      bannerIcon.innerHTML = '<i class="bi bi-exclamation-triangle-fill text-danger"></i>';
      showToast('System is in an UNSAFE state!', 'warning');
    }

    renderTrace(data.steps || []);
    document.getElementById('trace-step-count').innerText = `${(data.steps || []).length} Steps Recorded`;
    updateGlobalStatus();

  } catch (err) {
    showToast('Failed to run safety algorithm: ' + err, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-play-circle-fill me-1"></i> RUN SAFETY ALGORITHM';
  }
}

function renderTrace(steps) {
  const container = document.getElementById('safety-trace-container');
  if (!steps || steps.length === 0) {
    container.innerHTML = '<div class="alert alert-info">No processes evaluated. Add processes to the system.</div>';
    return;
  }

  container.innerHTML = steps.map(s => {
    const isCanFinish = s.can_finish;
    const badgeColor = isCanFinish ? 'bg-success' : 'bg-danger';
    const statusText = isCanFinish ? 'CAN FINISH (Need &le; Work)' : 'CANNOT FINISH (Need > Work)';

    const workBeforeStr = Object.entries(s.work_before || {}).map(([r, v]) => `${r}:${v}`).join(', ');
    const needStr = Object.entries(s.need || {}).map(([r, v]) => `${r}:${v}`).join(', ');
    const allocStr = Object.entries(s.allocation || {}).map(([r, v]) => `${r}:${v}`).join(', ');
    const workAfterStr = Object.entries(s.work_after || {}).map(([r, v]) => `${r}:${v}`).join(', ');

    return `
      <div class="step-item">
        <div class="step-badge">${s.step}</div>
        <div class="card p-3 border shadow-none bg-white">
          <div class="d-flex justify-content-between align-items-center mb-2">
            <h6 class="fw-bold mb-0">Evaluate Process <span class="badge bg-primary fs-6">${s.process}</span></h6>
            <span class="badge ${badgeColor}">${statusText}</span>
          </div>
          
          <div class="row g-2 small mb-2">
            <div class="col-sm-6 col-md-3">
              <span class="text-muted d-block">Work (Before):</span>
              <code>[${workBeforeStr}]</code>
            </div>
            <div class="col-sm-6 col-md-3">
              <span class="text-muted d-block">Need [${s.process}]:</span>
              <code>[${needStr}]</code>
            </div>
            <div class="col-sm-6 col-md-3">
              <span class="text-muted d-block">Allocation [${s.process}]:</span>
              <code>[${allocStr}]</code>
            </div>
            <div class="col-sm-6 col-md-3">
              <span class="text-muted d-block">Work (After):</span>
              <code class="fw-bold text-success">[${workAfterStr}]</code>
            </div>
          </div>

          <div class="small text-secondary">
            ${s.explanation || ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

document.addEventListener('DOMContentLoaded', loadSafetyInit);

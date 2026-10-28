const sampleScenarioSchema = {
  resources: [
    { resource_id: "R1", name: "Printer", total: 2 },
    { resource_id: "R2", name: "Tape Drive", total: 1 }
  ],
  processes: [
    { pid: "P1", name: "Job A", allocation: { R1: 1, R2: 0 }, maximum: { R1: 2, R2: 1 } },
    { pid: "P2", name: "Job B", allocation: { R1: 0, R2: 1 }, maximum: { R1: 1, R2: 1 } }
  ],
  requests: [
    { pid: "P1", request: { R1: 0, R2: 1 } },
    { pid: "P2", request: { R1: 1, R2: 0 } }
  ]
};

async function loadScenariosList() {
  try {
    const res = await fetch('/api/scenarios');
    const data = await res.json();

    const predefined = data.predefined || {};
    const custom = data.custom || [];

    // 1. Render Predefined Scenarios
    const preContainer = document.getElementById('predefined-scenarios-container');
    preContainer.innerHTML = Object.entries(predefined).map(([key, s]) => {
      const procCount = (s.processes || []).length;
      const resCount = (s.resources || []).length;
      const reqCount = (s.requests || []).length;

      let badgeType = 'badge bg-success-subtle text-success';
      if (key.includes('deadlock')) badgeType = 'badge bg-danger-subtle text-danger';
      else if (key.includes('unsafe')) badgeType = 'badge bg-warning-subtle text-warning text-dark';

      return `
        <div class="col-12 col-md-6 col-lg-4">
          <div class="card p-3 h-100 border shadow-none bg-white d-flex flex-column justify-content-between">
            <div>
              <div class="d-flex justify-content-between align-items-start mb-2">
                <h6 class="fw-bold mb-0 text-dark">${s.name}</h6>
                <span class="${badgeType}">${key}</span>
              </div>
              <p class="small text-muted mb-3" style="min-height: 48px;">${s.description}</p>
              
              <div class="small text-secondary mb-3">
                <span class="me-2"><i class="bi bi-cpu me-1"></i>${procCount} Processes</span>
                <span class="me-2"><i class="bi bi-hdd-stack me-1"></i>${resCount} Resources</span>
                ${reqCount > 0 ? `<span><i class="bi bi-send me-1"></i>${reqCount} Requests</span>` : ''}
              </div>
            </div>

            <button class="btn btn-outline-primary btn-sm w-100 fw-semibold" onclick="loadSpecificScenario('${key}')">
              <i class="bi bi-box-arrow-in-down me-1"></i> Load Scenario
            </button>
          </div>
        </div>
      `;
    }).join('');

    // 2. Render Custom Scenarios
    const customContainer = document.getElementById('custom-scenarios-container');
    if (custom.length === 0) {
      customContainer.innerHTML = '<p class="small text-muted mb-0">No custom scenarios saved yet. Use the "Custom Scenario JSON" button above to add one.</p>';
    } else {
      customContainer.innerHTML = `
        <div class="row g-3">
          ${custom.map(s => `
            <div class="col-md-6 col-lg-4">
              <div class="card p-3 border shadow-none bg-white">
                <h6 class="fw-bold mb-1">${s.name}</h6>
                <p class="small text-muted mb-2">${s.description || 'Custom configuration'}</p>
                <button class="btn btn-sm btn-outline-primary" onclick="loadSpecificScenario(${s.id})">
                  <i class="bi bi-box-arrow-in-down me-1"></i> Load Custom Scenario
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Populate modal textarea template
    const modalJson = document.getElementById('custom-scen-json');
    if (modalJson && !modalJson.value) {
      modalJson.value = JSON.stringify(sampleScenarioSchema, null, 2);
    }

  } catch (err) {
    showToast('Failed to load scenarios: ' + err, 'error');
  }
}

async function loadSpecificScenario(keyOrId) {
  try {
    const res = await fetch('/api/scenarios/load', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id: keyOrId })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Scenario loaded successfully.', 'success');
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to load scenario.', 'error');
    }
  } catch (err) {
    showToast('Load scenario error: ' + err, 'error');
  }
}

async function submitCustomScenario() {
  const name = document.getElementById('custom-scen-name').value.trim();
  const desc = document.getElementById('custom-scen-desc').value.trim();
  const jsonStr = document.getElementById('custom-scen-json').value.trim();

  if (!name) {
    showToast('Scenario name is required.', 'error');
    return;
  }

  let config;
  try {
    config = JSON.parse(jsonStr);
  } catch (e) {
    showToast('Invalid JSON syntax: ' + e.message, 'error');
    return;
  }

  try {
    const res = await fetch('/api/scenarios/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: desc, configuration: config })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Scenario saved.', 'success');
      bootstrap.Modal.getInstance(document.getElementById('customScenarioModal')).hide();
      loadScenariosList();
    } else {
      showToast(data.error || 'Failed to save scenario.', 'error');
    }
  } catch (err) {
    showToast('Save scenario error: ' + err, 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadScenariosList);

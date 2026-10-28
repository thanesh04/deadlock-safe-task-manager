/**
 * Deadlock-Aware CPU Scheduler Frontend Controller.
 * Handles interactive Gantt chart rendering, real-time clock step/play loops,
 * process table updates, anomaly risk scoring, and dual-engine log streaming.
 */

let playInterval = null;
const TICK_INTERVAL_MS = 650;

document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  loadSchedulerState();
});

function initEventListeners() {
  // Step Button (+1 Tick)
  const btnStep = document.getElementById('btn-step');
  if (btnStep) {
    btnStep.addEventListener('click', () => {
      pauseSimulation();
      stepSimulation();
    });
  }

  // Play Button
  const btnPlay = document.getElementById('btn-play');
  if (btnPlay) {
    btnPlay.addEventListener('click', () => {
      startPlayLoop();
    });
  }

  // Pause Button
  const btnPause = document.getElementById('btn-pause');
  if (btnPause) {
    btnPause.addEventListener('click', () => {
      pauseSimulation();
    });
  }

  // Run All Button
  const btnRunAll = document.getElementById('btn-run-all');
  if (btnRunAll) {
    btnRunAll.addEventListener('click', () => {
      pauseSimulation();
      runAllSimulation();
    });
  }

  // Reset Button
  const btnReset = document.getElementById('btn-reset');
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      pauseSimulation();
      resetSimulation();
    });
  }

  // Preset Selection Change
  const presetSelect = document.getElementById('sched-preset-select');
  if (presetSelect) {
    presetSelect.addEventListener('change', () => {
      pauseSimulation();
      reinitializeScheduler();
    });
  }

  // Policy Selection Change
  const policySelect = document.getElementById('sched-policy-select');
  if (policySelect) {
    policySelect.addEventListener('change', () => {
      const qCol = document.getElementById('quantum-col');
      if (qCol) {
        qCol.style.display = policySelect.value === 'RR' ? 'block' : 'none';
      }
      pauseSimulation();
      reinitializeScheduler();
    });
  }

  // Quantum Input Change
  const quantumInput = document.getElementById('sched-quantum-input');
  if (quantumInput) {
    quantumInput.addEventListener('change', () => {
      pauseSimulation();
      reinitializeScheduler();
    });
  }

  // Mode Selection Change
  const modeSelect = document.getElementById('sched-mode-select');
  if (modeSelect) {
    modeSelect.addEventListener('change', () => {
      pauseSimulation();
      reinitializeScheduler();
    });
  }

  // Aging Toggle Change
  const agingToggle = document.getElementById('aging-toggle');
  if (agingToggle) {
    agingToggle.addEventListener('change', () => {
      reinitializeScheduler();
    });
  }
}

function startPlayLoop() {
  const btnPlay = document.getElementById('btn-play');
  const btnPause = document.getElementById('btn-pause');
  if (btnPlay) btnPlay.classList.add('d-none');
  if (btnPause) btnPause.classList.remove('d-none');

  if (playInterval) clearInterval(playInterval);
  playInterval = setInterval(() => {
    stepSimulation(true);
  }, TICK_INTERVAL_MS);
}

function pauseSimulation() {
  if (playInterval) {
    clearInterval(playInterval);
    playInterval = null;
  }
  const btnPlay = document.getElementById('btn-play');
  const btnPause = document.getElementById('btn-pause');
  if (btnPlay) btnPlay.classList.remove('d-none');
  if (btnPause) btnPause.classList.add('d-none');
}

async function loadSchedulerState() {
  try {
    const res = await fetch('/api/scheduler/state');
    if (!res.ok) throw new Error('Failed to load scheduler state');
    const state = await res.json();
    renderUI(state);
  } catch (err) {
    console.error('Error fetching scheduler state:', err);
  }
}

async function stepSimulation(isFromPlay = false) {
  try {
    const res = await fetch('/api/scheduler/tick', { method: 'POST' });
    if (!res.ok) throw new Error('Tick error');
    const state = await res.json();
    renderUI(state);

    if (state.is_completed || state.is_deadlocked) {
      pauseSimulation();
    }
  } catch (err) {
    console.error('Error advancing clock tick:', err);
    pauseSimulation();
  }
}

async function runAllSimulation() {
  try {
    const res = await fetch('/api/scheduler/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ max_ticks: 60 })
    });
    if (!res.ok) throw new Error('Run all error');
    const state = await res.json();
    renderUI(state);
  } catch (err) {
    console.error('Error executing run all:', err);
  }
}

async function resetSimulation() {
  try {
    const res = await fetch('/api/scheduler/reset', { method: 'POST' });
    if (!res.ok) throw new Error('Reset error');
    const data = await res.json();
    renderUI(data.state);
  } catch (err) {
    console.error('Error resetting simulation:', err);
  }
}

async function reinitializeScheduler() {
  const preset = document.getElementById('sched-preset-select')?.value || 'balanced';
  const policy = document.getElementById('sched-policy-select')?.value || 'RR';
  const quantum = parseInt(document.getElementById('sched-quantum-input')?.value || '2', 10);
  const mode = document.getElementById('sched-mode-select')?.value || 'DEADLOCK_AWARE';
  const agingEnabled = document.getElementById('aging-toggle')?.checked ?? true;

  try {
    const res = await fetch('/api/scheduler/init', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        preset,
        policy,
        quantum,
        mode,
        aging_threshold: 3,
        aging_enabled: agingEnabled
      })
    });
    if (!res.ok) throw new Error('Init error');
    const data = await res.json();
    renderUI(data.state);
  } catch (err) {
    console.error('Error reinitializing scheduler:', err);
  }
}

function renderUI(state) {
  renderTopCards(state);
  renderGanttChart(state);
  renderProcessTable(state);
  renderLogs(state);
  renderMetrics(state);
}

function renderTopCards(state) {
  const clockEl = document.getElementById('sched-clock');
  const policySubEl = document.getElementById('sched-policy-sub');
  if (clockEl) clockEl.textContent = `T = ${state.clock}`;
  if (policySubEl) {
    const qStr = state.policy === 'RR' ? ` (q=${state.quantum})` : '';
    policySubEl.textContent = `Policy: ${state.policy}${qStr}`;
  }

  // CPU Dispatcher Card
  const currentTaskEl = document.getElementById('sched-current-task');
  const cpuSubEl = document.getElementById('sched-cpu-sub');
  if (currentTaskEl && cpuSubEl) {
    if (state.is_completed) {
      currentTaskEl.textContent = 'COMPLETED';
      currentTaskEl.className = 'stat-value mt-1 text-success';
      cpuSubEl.textContent = 'All tasks finished execution';
    } else if (state.is_deadlocked) {
      currentTaskEl.textContent = 'DEADLOCKED';
      currentTaskEl.className = 'stat-value mt-1 text-danger';
      cpuSubEl.textContent = 'Circular wait stall in Naive Mode';
    } else if (state.current_pid) {
      const task = state.tasks.find(t => t.pid === state.current_pid);
      currentTaskEl.textContent = state.current_pid;
      currentTaskEl.className = 'stat-value mt-1 text-primary';
      cpuSubEl.textContent = task ? `${task.name} (${task.remaining_burst} ticks left)` : 'Executing';
    } else {
      currentTaskEl.textContent = 'IDLE';
      currentTaskEl.className = 'stat-value mt-1 text-secondary';
      cpuSubEl.textContent = 'No eligible task ready to run';
    }
  }

  // Deadlocks Averted Card
  const avertedEl = document.getElementById('sched-averted-count');
  const modeSubEl = document.getElementById('sched-safety-mode');
  if (avertedEl) avertedEl.textContent = `${state.metrics.deadlocks_averted || 0}`;
  if (modeSubEl) {
    modeSubEl.textContent = state.mode === 'DEADLOCK_AWARE'
      ? 'Mode: Deadlock-Aware (Banker\'s)'
      : 'Mode: Naive (Zero Protection)';
  }

  // Aging & Starvation Card
  const agingEl = document.getElementById('sched-aging-count');
  const anomalySubEl = document.getElementById('sched-anomaly-sub');
  if (agingEl) {
    const totalBoosts = state.tasks.reduce((sum, t) => sum + (t.aging_boost || 0), 0);
    agingEl.textContent = `${totalBoosts} Boosted`;
  }
  if (anomalySubEl) {
    const critCount = (state.anomalies || []).filter(a => a.severity === 'CRITICAL' || a.severity === 'HIGH').length;
    anomalySubEl.textContent = critCount > 0 ? `${critCount} High-Risk Tasks` : '0 Critical Anomalies';
  }
}

function renderGanttChart(state) {
  const track = document.getElementById('gantt-track');
  const countBadge = document.getElementById('gantt-tick-count');
  if (!track) return;

  if (countBadge) {
    countBadge.textContent = `${state.gantt_timeline.length} ticks recorded`;
  }

  if (state.gantt_timeline.length === 0) {
    track.innerHTML = `<div class="text-muted p-3 small">Simulation ready at T=0. Click <strong>Step (+1)</strong> or <strong>Play</strong> to execute.</div>`;
    return;
  }

  track.innerHTML = '';
  state.gantt_timeline.forEach(slot => {
    const slotDiv = document.createElement('div');
    slotDiv.className = 'gantt-slot';

    if (slot.state === 'RUNNING') {
      slotDiv.classList.add('slot-running');
    } else if (slot.state === 'SAFETY_WAIT') {
      slotDiv.classList.add('slot-safety-wait');
    } else if (slot.state === 'DEADLOCKED') {
      slotDiv.classList.add('slot-deadlocked');
    } else {
      slotDiv.classList.add('slot-idle');
    }

    slotDiv.innerHTML = `
      <div class="gantt-tick-lbl">T=${slot.tick}</div>
      <div>${slot.pid}</div>
    `;

    slotDiv.title = `[T=${slot.tick}] ${slot.pid} (${slot.state}): ${slot.note || ''}`;

    slotDiv.addEventListener('click', () => {
      const inspector = document.getElementById('gantt-slot-inspector');
      const tickEl = document.getElementById('inspector-tick');
      const descEl = document.getElementById('inspector-desc');
      if (inspector && tickEl && descEl) {
        inspector.classList.remove('d-none');
        tickEl.textContent = `Tick T=${slot.tick} [${slot.pid}]`;
        descEl.textContent = `${slot.note || 'Executed cycle on CPU.'} (State: ${slot.state})`;
      }
    });

    track.appendChild(slotDiv);
  });

  // Auto-scroll track to the end so user sees the progress live
  const scrollWrapper = document.getElementById('gantt-container');
  if (scrollWrapper) {
    scrollWrapper.scrollLeft = scrollWrapper.scrollWidth;
  }
}

function renderProcessTable(state) {
  const tbody = document.getElementById('sched-tasks-tbody');
  if (!tbody) return;

  tbody.innerHTML = '';
  const anomalyMap = {};
  (state.anomalies || []).forEach(a => { anomalyMap[a.pid] = a; });

  state.tasks.forEach(task => {
    const anom = anomalyMap[task.pid] || {};
    const tr = document.createElement('tr');

    // Progress percentage
    const pct = task.burst_time > 0
      ? Math.round((task.progress_burst / task.burst_time) * 100)
      : 0;

    // State badge
    let stateBadge = `<span class="badge bg-secondary">${task.state}</span>`;
    if (task.state === 'RUNNING') {
      stateBadge = `<span class="badge bg-primary">RUNNING</span>`;
    } else if (task.state === 'READY') {
      stateBadge = `<span class="badge bg-info text-dark">READY</span>`;
    } else if (task.state === 'SAFETY_WAIT') {
      stateBadge = `<span class="badge bg-warning text-dark">SAFETY_WAIT</span>`;
    } else if (task.state === 'DEADLOCKED') {
      stateBadge = `<span class="badge bg-danger">DEADLOCKED</span>`;
    } else if (task.state === 'TERMINATED') {
      stateBadge = `<span class="badge bg-success">TERMINATED</span>`;
    }

    // Priority badge (with aging boost)
    let prioDisplay = `P${task.priority}`;
    if (task.aging_boost > 0) {
      prioDisplay += ` <span class="badge bg-warning text-dark" title="Aging Boost">+${task.aging_boost} Boost</span>`;
    }

    // Held resources
    const heldList = Object.entries(task.held_resources || {})
      .filter(([_, val]) => val > 0)
      .map(([res, val]) => `${res}:${val}`)
      .join(', ') || '<span class="text-muted">None</span>';

    // Starvation
    const starvDisplay = task.starvation_ticks > 0
      ? `<span class="text-danger fw-bold">${task.starvation_ticks} ticks</span>`
      : `<span class="text-muted">0</span>`;

    // Behavior & Anomaly badge
    let riskBadge = `<span class="badge badge-risk-normal">Normal</span>`;
    if (anom.severity === 'CRITICAL' || anom.severity === 'HIGH') {
      riskBadge = `<span class="badge badge-risk-critical" title="${anom.description}">${anom.description || 'Critical Risk'}</span>`;
    } else if (anom.severity === 'WARNING') {
      riskBadge = `<span class="badge badge-risk-warning" title="${anom.description}">${anom.description || 'Warning'}</span>`;
    }

    const greedStr = anom.greed_index !== undefined ? `${anom.greed_index}% Greed` : '';

    tr.innerHTML = `
      <td class="fw-bold">${task.pid}</td>
      <td>${task.name}</td>
      <td>${stateBadge}</td>
      <td style="min-width: 140px;">
        <div class="d-flex justify-content-between text-muted" style="font-size: 0.72rem;">
          <span>${task.progress_burst}/${task.burst_time}</span>
          <span>${pct}%</span>
        </div>
        <div class="progress" style="height: 5px;">
          <div class="progress-bar ${task.state === 'TERMINATED' ? 'bg-success' : 'bg-primary'}" style="width: ${pct}%"></div>
        </div>
      </td>
      <td>${prioDisplay}</td>
      <td>${heldList}</td>
      <td>${starvDisplay}</td>
      <td>
        <div class="d-flex flex-column gap-1">
          <div>${riskBadge}</div>
          <small class="text-muted" style="font-size: 0.68rem;">${greedStr}</small>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderLogs(state) {
  const feed = document.getElementById('scheduler-logs');
  if (!feed) return;

  if (!state.event_logs || state.event_logs.length === 0) {
    feed.innerHTML = `<div class="text-muted small">[T=00] Ready to simulate.</div>`;
    return;
  }

  feed.innerHTML = '';
  state.event_logs.forEach(log => {
    const entry = document.createElement('div');
    entry.className = 'log-entry';

    let catBg = 'bg-secondary';
    if (log.category === 'BANKERS_SAFE') catBg = 'bg-success text-white';
    else if (log.category === 'BANKERS_UNSAFE') catBg = 'bg-warning text-dark';
    else if (log.category === 'DEADLOCK') catBg = 'bg-danger text-white';
    else if (log.category === 'AGING') catBg = 'bg-info text-dark';
    else if (log.category === 'DISPATCHER') catBg = 'bg-primary text-white';

    entry.innerHTML = `
      <span class="log-tick">[T=${String(log.tick).padStart(2, '0')}]</span>
      <span class="log-category ${catBg}">${log.category}</span>
      <span>${log.message}</span>
    `;
    feed.appendChild(entry);
  });

  feed.scrollTop = feed.scrollHeight;
}

function renderMetrics(state) {
  const m = state.metrics || {};
  const utilEl = document.getElementById('metric-cpu-util');
  const turnEl = document.getElementById('metric-turnaround');
  const waitEl = document.getElementById('metric-waiting');
  const csEl = document.getElementById('metric-context-switches');

  if (utilEl) utilEl.textContent = `${m.cpu_utilization_percent || 0}%`;
  if (turnEl) turnEl.textContent = `${m.average_turnaround_time || 0} ticks`;
  if (waitEl) waitEl.textContent = `${m.average_waiting_time || 0} ticks`;
  if (csEl) csEl.textContent = `${m.context_switches || 0}`;
}

async function loadMatrices() {
  try {
    const res = await fetch('/api/matrices');
    const data = await res.json();

    const processes = data.processes || [];
    const resources = data.resources || [];
    const available = data.available || {};
    const allocation = data.allocation || {};
    const maximum = data.maximum || {};
    const need = data.need || {};

    // 1. Available Vector
    const availHead = document.getElementById('avail-matrix-head');
    const availBody = document.getElementById('avail-matrix-body');

    availHead.innerHTML = `<tr>${resources.map(r => `<th>${r}</th>`).join('')}</tr>`;
    availBody.innerHTML = `<tr>${resources.map(r => `<td><strong class="text-success fs-5">${available[r] ?? 0}</strong></td>`).join('')}</tr>`;

    // Helper to render 2D matrix
    function render2D(headId, bodyId, matrixData, badgeClass = '') {
      const head = document.getElementById(headId);
      const body = document.getElementById(bodyId);

      head.innerHTML = `<tr><th>Process</th>${resources.map(r => `<th>${r}</th>`).join('')}</tr>`;

      if (processes.length === 0) {
        body.innerHTML = `<tr><td colspan="${resources.length + 1}" class="text-center text-muted">No processes available</td></tr>`;
        return;
      }

      body.innerHTML = processes.map(p => {
        const rowCells = resources.map(r => {
          const val = matrixData[p] ? (matrixData[p][r] ?? 0) : 0;
          return `<td><span class="${badgeClass}">${val}</span></td>`;
        }).join('');
        return `<tr><td class="fw-bold bg-light">${p}</td>${rowCells}</tr>`;
      }).join('');
    }

    // 2. Allocation Matrix
    render2D('alloc-matrix-head', 'alloc-matrix-body', allocation, 'badge bg-primary text-white px-2 py-1');

    // 3. Maximum Matrix
    render2D('max-matrix-head', 'max-matrix-body', maximum, 'fw-semibold text-dark');

    // 4. Need Matrix
    render2D('need-matrix-head', 'need-matrix-body', need, 'badge bg-warning text-dark px-2 py-1');

  } catch (err) {
    showToast('Failed to load system matrices: ' + err, 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadMatrices);

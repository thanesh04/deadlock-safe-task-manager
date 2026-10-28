let resourcesList = [];

async function loadResources() {
  try {
    const res = await fetch('/api/resources');
    resourcesList = await res.json();

    const tbody = document.getElementById('resources-table-body');
    if (!resourcesList || resourcesList.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No resources defined yet.</td></tr>';
      return;
    }

    tbody.innerHTML = resourcesList.map(r => {
      let progressColor = 'bg-success';
      if (r.utilization_percent > 85) progressColor = 'bg-danger';
      else if (r.utilization_percent > 60) progressColor = 'bg-warning text-dark';

      return `
        <tr>
          <td><strong class="font-monospace">${r.resource_id}</strong></td>
          <td>${r.name}</td>
          <td>${r.total_instances}</td>
          <td><span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">${r.available_instances}</span></td>
          <td><span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1">${r.allocated_instances}</span></td>
          <td style="min-width: 160px;">
            <div class="d-flex align-items-center gap-2">
              <div class="progress flex-grow-1" style="height: 8px;">
                <div class="progress-bar ${progressColor}" style="width: ${r.utilization_percent}%;"></div>
              </div>
              <span class="small fw-semibold text-muted">${r.utilization_percent}%</span>
            </div>
          </td>
          <td class="text-end">
            <div class="btn-group btn-group-sm">
              <button class="btn btn-outline-secondary" onclick="openEditModal(${r.id})" title="Edit Resource">
                <i class="bi bi-pencil"></i>
              </button>
              <button class="btn btn-outline-danger" onclick="deleteResource(${r.id})" title="Delete Resource">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    showToast('Failed to load resources: ' + err, 'error');
  }
}

async function submitCreateResource() {
  const rid = document.getElementById('new-res-id').value.trim();
  const name = document.getElementById('new-res-name').value.trim();
  const total = parseInt(document.getElementById('new-res-total').value) || 1;

  if (!rid || !name) {
    showToast('Resource ID and Name are required.', 'error');
    return;
  }

  try {
    const res = await fetch('/api/resources', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resource_id: rid, name, total_instances: total })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Resource created.', 'success');
      bootstrap.Modal.getInstance(document.getElementById('createResourceModal')).hide();
      document.getElementById('createResourceForm').reset();
      loadResources();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to create resource.', 'error');
    }
  } catch (err) {
    showToast('Error creating resource: ' + err, 'error');
  }
}

function openEditModal(resId) {
  const res = resourcesList.find(r => r.id === resId);
  if (!res) return;

  document.getElementById('edit-res-id').value = res.id;
  document.getElementById('edit-res-name').value = res.name;
  document.getElementById('edit-res-total').value = res.total_instances;

  const modal = new bootstrap.Modal(document.getElementById('editResourceModal'));
  modal.show();
}

async function submitEditResource() {
  const resId = document.getElementById('edit-res-id').value;
  const name = document.getElementById('edit-res-name').value.trim();
  const total = parseInt(document.getElementById('edit-res-total').value) || 1;

  try {
    const res = await fetch(`/api/resources/${resId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, total_instances: total })
    });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Resource updated.', 'success');
      bootstrap.Modal.getInstance(document.getElementById('editResourceModal')).hide();
      loadResources();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to update resource.', 'error');
    }
  } catch (err) {
    showToast('Error updating resource: ' + err, 'error');
  }
}

async function deleteResource(resId) {
  if (!confirm('Are you sure you want to delete this resource? Note: Resources with active allocations cannot be deleted.')) return;
  try {
    const res = await fetch(`/api/resources/${resId}`, { method: 'DELETE' });
    const data = await res.json();
    if (res.ok) {
      showToast(data.message || 'Resource deleted.', 'success');
      loadResources();
      updateGlobalStatus();
    } else {
      showToast(data.error || 'Failed to delete resource.', 'error');
    }
  } catch (err) {
    showToast('Error deleting resource: ' + err, 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadResources);

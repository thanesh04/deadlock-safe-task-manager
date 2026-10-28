let cy = null;
let graphData = null;
let currentMode = 'rag'; // 'rag' or 'wfg'

const cyStyle = [
  // Process Node
  {
    selector: 'node[type="process"]',
    style: {
      'shape': 'ellipse',
      'background-color': '#2563eb',
      'label': 'data(label)',
      'color': '#1e293b',
      'font-size': '12px',
      'font-weight': 'bold',
      'text-valign': 'top',
      'text-margin-y': -8,
      'width': 44,
      'height': 44,
      'border-width': 2,
      'border-color': '#1d4ed8'
    }
  },
  // Deadlocked or Cycle Process Node
  {
    selector: 'node[is_deadlocked = true], node[in_cycle = true]',
    style: {
      'background-color': '#ef4444',
      'border-color': '#b91c1c',
      'border-width': 4
    }
  },
  // Resource Node
  {
    selector: 'node[type="resource"]',
    style: {
      'shape': 'round-rectangle',
      'background-color': '#10b981',
      'label': 'data(label)',
      'color': '#064e3b',
      'font-size': '11px',
      'font-weight': 'bold',
      'text-valign': 'top',
      'text-margin-y': -8,
      'text-wrap': 'wrap',
      'width': 60,
      'height': 44,
      'border-width': 2,
      'border-color': '#059669'
    }
  },
  // Edges - Normal
  {
    selector: 'edge',
    style: {
      'width': 2.5,
      'curve-style': 'bezier',
      'target-arrow-shape': 'triangle',
      'arrow-scale': 1.2,
      'font-size': '10px',
      'label': 'data(label)',
      'text-rotation': 'autorotate',
      'text-margin-y': -6
    }
  },
  // Allocation Edge (Resource -> Process)
  {
    selector: 'edge[edge_type="allocation"]',
    style: {
      'line-color': '#3b82f6',
      'target-arrow-color': '#3b82f6'
    }
  },
  // Request Edge (Process -> Resource)
  {
    selector: 'edge[edge_type="request"]',
    style: {
      'line-color': '#f59e0b',
      'target-arrow-color': '#f59e0b',
      'line-style': 'dashed'
    }
  },
  // Cycle Highlighted Edge
  {
    selector: 'edge[in_cycle = true]',
    style: {
      'line-color': '#ef4444',
      'target-arrow-color': '#ef4444',
      'width': 4.5,
      'line-style': 'solid'
    }
  },
  // Selected Node
  {
    selector: ':selected',
    style: {
      'border-width': 4,
      'border-color': '#000000',
      'shadow-blur': 10,
      'shadow-color': 'rgba(0,0,0,0.3)'
    }
  }
];

async function initGraphView() {
  try {
    const res = await fetch('/api/graphs');
    graphData = await res.json();
    renderGraph();
    renderCycleInfo();
  } catch (err) {
    showToast('Failed to load graph data: ' + err, 'error');
  }
}

function renderGraph() {
  const elements = currentMode === 'rag' ? (graphData.rag_elements || []) : (graphData.wfg_elements || []);

  if (cy) {
    cy.destroy();
  }

  cy = cytoscape({
    container: document.getElementById('cy-container'),
    elements: elements,
    style: cyStyle,
    layout: {
      name: 'cose',
      animate: false,
      padding: 50,
      nodeRepulsion: 600000,
      idealEdgeLength: 120
    }
  });

  // Node Click Inspector
  cy.on('tap', 'node', function(evt) {
    const node = evt.target;
    const data = node.data();
    const inspector = document.getElementById('node-inspector');

    if (data.type === 'process') {
      inspector.innerHTML = `
        <div class="fw-bold text-dark mb-1">${data.label}</div>
        <div><strong>Type:</strong> Simulated Process</div>
        <div><strong>Status:</strong> ${data.state}</div>
        <div><strong>In Deadlock:</strong> ${data.is_deadlocked ? '<span class="text-danger fw-bold">YES</span>' : 'No'}</div>
        <div><strong>Part of Cycle:</strong> ${data.in_cycle ? '<span class="text-danger fw-bold">YES</span>' : 'No'}</div>
      `;
    } else {
      inspector.innerHTML = `
        <div class="fw-bold text-dark mb-1">${data.label}</div>
        <div><strong>Type:</strong> Multi-Instance Resource</div>
        <div><strong>Total Units:</strong> ${data.total}</div>
        <div><strong>Available Units:</strong> ${data.available}</div>
        <div><strong>Currently Allocated:</strong> ${data.total - data.available}</div>
      `;
    }
  });
}

function renderCycleInfo() {
  const container = document.getElementById('cycle-alert-container');
  const cycles = graphData.cycles || [];

  if (cycles.length === 0) {
    container.innerHTML = `
      <div class="alert alert-success py-2 px-3 small mb-0">
        <i class="bi bi-check-circle me-1"></i> No circular wait detected in the current state.
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="alert alert-danger py-2 px-3 small mb-2">
        <i class="bi bi-exclamation-octagon-fill me-1"></i>
        <strong>${cycles.length} Cycle(s) Detected!</strong>
      </div>
      <div class="list-group list-group-flush border rounded small">
        ${cycles.map((c, i) => `
          <div class="list-group-item py-1">
            <span class="text-muted">Cycle ${i + 1}:</span>
            <code class="text-danger fw-bold d-block mt-1">${c.join(' &rarr; ')}</code>
          </div>
        `).join('')}
      </div>
    `;
  }
}

function switchGraph(mode) {
  currentMode = mode;
  document.getElementById('tab-rag-btn').className = 'nav-link fw-semibold ' + (mode === 'rag' ? 'active' : '');
  document.getElementById('tab-wfg-btn').className = 'nav-link fw-semibold ' + (mode === 'wfg' ? 'active' : '');
  renderGraph();
}

function fitGraph() {
  if (cy) cy.fit();
}

function zoomIn() {
  if (cy) cy.zoom(cy.zoom() * 1.25);
}

function zoomOut() {
  if (cy) cy.zoom(cy.zoom() * 0.8);
}

function relayoutGraph() {
  if (cy) {
    cy.layout({
      name: 'cose',
      animate: true,
      animationDuration: 400,
      padding: 50
    }).run();
  }
}

document.addEventListener('DOMContentLoaded', initGraphView);

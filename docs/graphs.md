  # Graph Visualization: Resource Allocation Graph & Wait-For Graph

Visualizing process-resource dependencies is one of the most effective ways to understand deadlocks.

This application uses **Cytoscape.js** (an industry-standard graph visualization library) to generate dynamic, interactive directed graphs on the **Graphs** page (`/graphs`).

---

## 1. Resource Allocation Graph (RAG)

A **Resource Allocation Graph (RAG)** is a directed bipartite graph that represents the complete allocation and request state of an operating system.

### Node Definitions:
- **Process Nodes**: Rendered as **blue circles** (e.g., $P_1, P_2$). If a process is deadlocked, it is colored in **pulsing red**.
- **Resource Nodes**: Rendered as **green rounded rectangles** (e.g., $R_1, R_2$). Each node displays its current available vs. total capacity (e.g., `Avail: 0/1`).

### Edge Definitions:
1. **Assignment Edge ($R_j \to P_i$)**:
   - Drawn as a **solid blue directed arrow** from a Resource to a Process.
   - **Meaning**: An instance of resource $R_j$ has been allocated to, and is currently held by, process $P_i$.
2. **Request Edge ($P_i \to R_j$)**:
   - Drawn as a **dashed yellow directed arrow** from a Process to a Resource.
   - **Meaning**: Process $P_i$ is currently waiting to acquire an instance of resource $R_j$.

```
 [Resource R1] ──────(Allocated to)──────► (Process P1)
       ▲                                         │
       │                                         │
 (Requests)                                  (Requests)
       │                                         │
       │                                         ▼
 (Process P2) ◄─────(Allocated to)─────── [Resource R2]
```

---

## 2. Wait-For Graph (WFG)

A **Wait-For Graph (WFG)** is a simplified graph obtained by removing the resource nodes from a Resource Allocation Graph and collapsing edges into process-to-process dependencies.

### Node Definitions:
- Contains **only Process nodes** (circles).

### Edge Definitions:
- **Directed Edge ($P_i \to P_j$)**:
  - Drawn as a directed arrow from process $P_i$ to process $P_j$.
  - **Meaning**: Process $P_i$ is waiting for a resource that is currently allocated to and held by process $P_j$.

```
     (Process P1) ──────────(Waiting for P2)──────────► (Process P2)
          ▲                                                   │
          │                                                   │
          └─────────────────(Waiting for P1)──────────────────┘
```

---

## 3. How Deadlock Cycles are Detected and Highlighted

### Cycle Definition:
A cycle is a closed directed path where a process can follow arrows and return to itself:
$$P_1 \to P_2 \to \dots \to P_k \to P_1$$

### Theoretical Significance:
- In systems with **single-instance resources**, a cycle in the RAG or WFG is **both necessary and sufficient** for a deadlock to exist.
- In systems with **multiple-instance resources**, a cycle is a **necessary condition**, but may not always be sufficient (unless all instances of the resource are trapped within the cycle).

### How the Application Detects Cycles:
In `algorithms/wait_for_graph.py`, the `WaitForGraph` class:
1. Iterates through all processes and resources to construct an adjacency list:
   - For every process $P_i$ requesting resource $R_k$, if process $P_j$ holds $R_k$, add edge $P_i \to P_j$.
2. Uses **Depth-First Search (DFS)** with path tracking to detect all directed simple cycles.
3. Canonicalizes each cycle (rotates so the lexicographically smallest PID is first) to eliminate duplicate representations of the same cycle.
4. Highlights the cycle edges in Cytoscape.js with **bold red lines** (`#ef4444`) and tags the nodes with `is_deadlocked: true`.

---

## 4. How the Application Builds Graphs (Not from Windows Kernel)

- **Source of Data**: When you view `/graphs`, the frontend calls `GET /api/graphs`.
- **Coordinator**: `Simulator.get_graphs_data()` in `simulation/simulator.py` extracts the current in-memory allocation and request matrices from the SQLite database.
- **Formatter**: `GraphBuilder` in `algorithms/graph_builder.py` formats these matrices into Cytoscape.js JSON elements:
  ```json
  [
    { "data": { "id": "proc_P1", "label": "P1", "type": "process", "is_deadlocked": true } },
    { "data": { "id": "res_R1", "label": "R1 (Avail: 0/1)", "type": "resource" } },
    { "data": { "id": "alloc_R1_P1", "source": "res_R1", "target": "proc_P1", "edge_type": "allocation" } },
    { "data": { "id": "req_P1_R2", "source": "proc_P1", "target": "res_R2", "edge_type": "request", "in_cycle": true } }
  ]
  ```
- **Renderer**: Cytoscape.js renders the interactive canvas using the force-directed `cose` layout algorithm.
- **Interactive Controls**: Users can pan, zoom, click **Fit**, click **Layout** to rearrange nodes, and click on any node to open the **Node Inspector** showing its allocations and requests.
- **Kernel Independence**: The graph **never** inspects Windows kernel driver locks, mutexes, or physical memory pointers. It visualizes the simulated database state.

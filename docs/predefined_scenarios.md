# Predefined Scenarios Catalog & Demonstration Presets

## 1. What is the Predefined Scenarios Catalog?

The **Predefined Scenarios Catalog** (located on the **Scenarios & Demos** page at `/scenarios`) is a collection of 7 curated Operating Systems textbook scenarios.

### Why Does It Exist?
During an academic viva or project demonstration, students cannot spend 10 minutes typing in matrices for 5 processes and 3 resources by hand. If a single number is typed incorrectly, the algorithm might yield an unexpected result. 

The catalog provides **deterministic, 1-click test configurations** that instantly load well-known Operating Systems textbook problems into the database so you can demonstrate the algorithms with 100% confidence.

> **ACADEMIC NOTE**: These scenarios are predefined input datasets stored in `simulation/scenarios.py`. The algorithm results (such as safe sequences or deadlock flags) are **NEVER hardcoded**—they are computed dynamically in real time from the loaded matrices.

---

## 2. Detailed Breakdown of the 7 Built-In Scenarios

---

### Scenario 1: Classic Safe State (`safe_state`)

- **Purpose**: Demonstrates Dijkstra's Banker's Safety Algorithm on the standard Silberschatz Operating Systems textbook example.
- **Processes (5)**:
  - $P_0$ (Web Server): Alloc = $[0, 1, 0]$, Max = $[7, 5, 3]$, Need = $[7, 4, 3]$
  - $P_1$ (Database Worker): Alloc = $[2, 0, 0]$, Max = $[3, 2, 2]$, Need = $[1, 2, 2]$
  - $P_2$ (Analytics Engine): Alloc = $[3, 0, 2]$, Max = $[9, 0, 2]$, Need = $[6, 0, 0]$
  - $P_3$ (Cache Service): Alloc = $[2, 1, 1]$, Max = $[2, 2, 2]$, Need = $[0, 1, 1]$
  - $P_4$ (Backup Agent): Alloc = $[0, 0, 2]$, Max = $[4, 3, 3]$, Need = $[4, 3, 1]$
- **Resources (3)**:
  - $R_0$ (CPU Core, Total = 10, Available = 3)
  - $R_1$ (Memory GB, Total = 5, Available = 3)
  - $R_2$ (Disk Channel, Total = 7, Available = 2)
- **Pending Requests**: None.
- **Expected Result**: **SAFE STATE**.
- **Safe Execution Sequence**: $\mathbf{P_1 \to P_3 \to P_0 \to P_2 \to P_4}$ (or alternate valid permutations).
- **What to Click**: Click **Demo Safe State** in topbar, then click **RUN SAFETY ALGORITHM** on `/safety`.
- **What Teacher Observes**: A green banner appears showing the safe sequence, accompanied by an educational trace explaining why each process finishes and adds its allocation back to the Work pool.

---

### Scenario 2: Unsafe State (`unsafe_state`)

- **Purpose**: Demonstrates an unsafe state where available resources are too low to satisfy any process's remaining maximum claim.
- **Processes (5)**: $P_0, P_1, P_2, P_3, P_4$.
- **Resources (3)**: $R_0$ (Total=10, Avail=0), $R_1$ (Total=5, Avail=0), $R_2$ (Total=7, Avail=0).
- **Expected Result**: **UNSAFE STATE**.
- **What to Click**: Click **Demo Unsafe State** in topbar, then click **RUN SAFETY ALGORITHM** on `/safety`.
- **What Teacher Observes**: A warning/danger banner appears stating: *"System is in an UNSAFE state. No complete safe sequence exists."* The trace lists which processes are blocked and their resource deficits.

---

### Scenario 3: Two-Process Circular Deadlock (`two_process_deadlock`)

- **Purpose**: Demonstrates the classic mutual hold-and-wait deadlock condition between two processes and single-unit resources.
- **Processes (2)**:
  - $P_1$: Holds $R_1$, requests $R_2$.
  - $P_2$: Holds $R_2$, requests $R_1$.
- **Resources (2)**:
  - $R_1$ (Scanner, Total = 1, Available = 0)
  - $R_2$ (Printer, Total = 1, Available = 0)
- **Active Requests**:
  - $P_1$ requests $[0, 1]$ ($R_2$).
  - $P_2$ requests $[1, 0]$ ($R_1$).
- **Expected Result**: **DEADLOCK DETECTED! Deadlocked: P1, P2**.
- **What to Click**: Click **Demo Deadlock** in topbar, then navigate to **Deadlock Detection** (`/deadlock-detection`) or **Graphs** (`/graphs`).
- **What Teacher Observes**:
  - On the detection page: A bright red alert identifies $P_1$ and $P_2$ as permanently blocked.
  - On the graphs page: Cytoscape renders a closed cycle highlighted in bold red ($P_1 \to P_2 \to P_1$).

---

### Scenario 4: Three-Process Circular Deadlock (`three_process_deadlock`)

- **Purpose**: Demonstrates a larger 3-node circular wait dependency.
- **Processes (3)**:
  - $P_1$ (Task Alpha): Holds $R_1$, requests $R_2$.
  - $P_2$ (Task Beta): Holds $R_2$, requests $R_3$.
  - $P_3$ (Task Gamma): Holds $R_3$, requests $R_1$.
- **Resources (3)**: $R_1, R_2, R_3$ (1 unit each, all 0 available).
- **Expected Result**: **DEADLOCK DETECTED! Deadlocked: P1, P2, P3**.
- **Detected Cycle**: $P_1 \to P_2 \to P_3 \to P_1$.
- **What to Click**: Click **Demo 3-Process Circular Deadlock** from the Demo Mode menu, then open `/graphs`.
- **What Teacher Observes**: A 3-node triangle cycle displayed on the Wait-For Graph in red.

---

### Scenario 5: Safely Granted Resource Request (`accepted_request`)

- **Purpose**: Demonstrates how Banker's Resource-Request algorithm evaluates a valid, safe request and safely commits it.
- **Initial State**: Classic safe state.
- **Request**: Process $P_1$ requests $[R_0=1, R_1=0, R_2=2]$.
- **Evaluation**:
  - Step 1: $[1, 0, 2] \le Need[P_1][1, 2, 2]$? **PASSED.**
  - Step 2: $[1, 0, 2] \le Available[3, 3, 2]$? **PASSED.**
  - Step 3: Tentative Available becomes $[2, 3, 0]$.
  - Step 4: Safety Algorithm finds safe sequence. **SAFE.**
  - Step 5: **REQUEST GRANTED** and committed.
- **What to Click**: Click **Demo Resource Request** in topbar, which takes you to `/resource-request`. Click **Evaluate & Allocate Request**.
- **What Teacher Observes**: The 5-step stepper marks all steps in green and commits the new allocation to $P_1$.

---

### Scenario 6: Denied Resource Request (`rejected_request`)

- **Purpose**: Proves that Banker's Algorithm prevents unsafe transitions even when resources are physically available.
- **Initial State**: Safe state with Available $R_1 = 3$.
- **Request**: Process $P_0$ requests $[R_0=0, R_1=3, R_2=0]$.
- **Evaluation**:
  - Step 1: $[0, 3, 0] \le Need[P_0][7, 4, 3]$? **PASSED.**
  - Step 2: $[0, 3, 0] \le Available[3, 3, 2]$? **PASSED** (3 units available).
  - Step 3: Tentative Available becomes $[3, 0, 2]$.
  - Step 4: Available Memory is now 0. Every single process needs at least 1 unit of memory to finish. No safe sequence exists. **UNSAFE.**
  - Step 5: **REQUEST DENIED** and rolled back!
- **What Teacher Observes**: The system catches the hazard and prevents the allocation, saving the system from entering an unsafe state.

---

### Scenario 7: Deadlock Recovery Scenario (`deadlock_recovery`)

- **Purpose**: Demonstrates resolving an active deadlock via process termination or simulated resource preemption.
- **Processes (3)**: $P_1$ (ML Training Job), $P_2$ (Query Engine), $P_3$ (ETL Pipeline).
- **Resources (2)**: $R_1$ (GPU Unit, Total=2), $R_2$ (Database Connection, Total=2).
- **Initial State**: $P_1$ and $P_2$ are deadlocked.
- **What to Click**: Click **Demo Deadlock Recovery**, navigate to `/deadlock-detection`. In the recovery panel, select $P_1$ and click **Terminate Victim**.
- **What Teacher Observes**:
  - $P_1$ is terminated and its held GPU units are returned to Available.
  - The detection algorithm re-runs automatically.
  - The banner switches from red to green: **DEADLOCK RESOLVED!**

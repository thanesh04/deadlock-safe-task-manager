# Banker's Resource-Request Algorithm: Step-by-Step Flow

When a simulated process wants additional resources during runtime, it cannot simply take them. The operating system must evaluate whether granting that request immediately could compromise system safety.

This document explains what happens under the hood when you use the **Resource Request** page (`/resource-request`) in this application.

---

## 1. What Happens When You Click "Evaluate & Allocate Request"?

When you select a process (e.g., $P_1$), enter resource values (e.g., $R_0=1, R_1=0, R_2=2$), and click **Evaluate & Allocate Request**:
1. Vanilla JavaScript collects the vector and makes a `POST` request to `/api/resource-request` with payload:
   ```json
   {
     "pid": "P1",
     "request": { "R0": 1, "R1": 0, "R2": 2 }
   }
   ```
2. Flask dispatches this call to `Simulator.process_resource_request()` in `simulation/simulator.py`.
3. The simulator initializes `ResourceRequestAlgorithm` from `algorithms/resource_request.py`.
4. The algorithm executes a strict **5-Step Decision Procedure**.

---

## 2. The 5-Step Evaluation Procedure

```
                     User Request Vector (Request_i)
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │ Step 1: Is Request_i <= Need_i for all resources?      │
       └────────────────────────────┬───────────────────────────┘
                     YES            │            NO
                      ┌─────────────┴─────────────┐
                      ▼                           ▼
       ┌──────────────────────────────┐ ┌──────────────────────┐
       │ Step 2: Request_i <= Avail?  │ │ DENIED: Exceeded Max │
       └──────────────┬───────────────┘ └──────────────────────┘
             YES      │      NO
              ┌───────┴───────┐
              ▼               ▼
       ┌──────────────┐ ┌───────────────────────────┐
       │ Step 3:      │ │ DENIED / WAIT:            │
       │ Tentative    │ │ Insufficient Availability │
       │ Allocation   │ └───────────────────────────┘
       └──────┬───────┘
              │
              ▼
       ┌────────────────────────────────────────────────────────┐
       │ Step 4: Run Banker's Safety Algorithm on Tentative     │
       └────────────────────────────┬───────────────────────────┘
                    SAFE            │          UNSAFE
                      ┌─────────────┴─────────────┐
                      ▼                           ▼
       ┌──────────────────────────────┐ ┌──────────────────────┐
       │ Step 5: COMMIT ALLOCATION    │ │ Step 5: ROLLBACK     │
       │ - Update DB allocations      │ │ - Restore state      │
       │ - Decrement available        │ │ - Process waits      │
       │ - Status: REQUEST GRANTED    │ │ - Status: DENIED     │
       └──────────────────────────────┘ └──────────────────────┘
```

### Step 1: Maximum Claim Check ($\text{Request}_i \le \text{Need}_i$)
- **Question**: Has process $P_i$ asked for more resources than it initially declared as its remaining need?
- **Logic**:
  $$\text{For every resource } j, \quad \text{Request}_i[j] \le \text{Need}_i[j]$$
- **Outcome if Failed**:
  - Immediate denial.
  - Reason: *"Request exceeds remaining need. Error: Process has exceeded its maximum claim."*
  - The OS treats this as an illegal operation by the application.

### Step 2: Resource Availability Check ($\text{Request}_i \le \text{Available}$)
- **Question**: Does the system currently possess enough unallocated units in its free pool to satisfy the request right now?
- **Logic**:
  $$\text{For every resource } j, \quad \text{Request}_i[j] \le \text{Available}[j]$$
- **Outcome if Failed**:
  - Denial and wait state.
  - Reason: *"Insufficient available resources. Process must wait until resources are released."*
  - Process state transitions to `WAITING`.

### Step 3: Tentative State Simulation
- **Action**: If Steps 1 and 2 pass, the operating system **hypothetically pretends** to allocate the resources.
- It calculates modified vectors in memory without modifying the permanent database tables:
  $$\text{Available}' = \text{Available} - \text{Request}_i$$
  $$\text{Allocation}'_i = \text{Allocation}_i + \text{Request}_i$$
  $$\text{Need}'_i = \text{Need}_i - \text{Request}_i$$

### Step 4: Safety Verification Test
- **Action**: The system executes `SafetyAlgorithm` on the tentative state $(\text{Available}', \text{Allocation}', \text{Need}')$.
- It checks whether there is still at least one safe execution sequence in which all processes can finish without deadlocking.

### Step 5: Final Decision (Commit or Rollback)
- **If Safe**:
  - The request is **GRANTED**.
  - The tentative state is **committed** to the database: $P_i$'s allocation increases, available decreases, and process state becomes `RUNNING`.
  - UI displays a green badge: **REQUEST GRANTED**.
- **If Unsafe**:
  - The request is **DENIED**.
  - The tentative state is **rolled back** (discarded).
  - The system remains in its prior safe state, and $P_i$ enters `WAITING`.
  - UI displays a red badge: **REQUEST DENIED (Avoided Unsafe State)**.

---

## 3. Concrete Example: Granted vs. Denied Requests

### Example 1: Safely Granted Request
- System Available: $[3, 3, 2]$
- Process $P_1$ requests: $[1, 0, 2]$
- $P_1$'s Need is $[1, 2, 2]$.
  - Step 1: $[1, 0, 2] \le [1, 2, 2]$? **PASSED.**
  - Step 2: $[1, 0, 2] \le [3, 3, 2]$? **PASSED.**
  - Step 3: Tentative Available becomes $[2, 3, 0]$.
  - Step 4: Safety algorithm finds sequence $\langle P_1, P_3, P_0, P_2, P_4 \rangle$. **SAFE.**
  - Step 5: Allocation is committed. System stays safe.

### Example 2: Denied Request (Avoids Unsafe State)
- System Available: $[3, 3, 2]$
- Process $P_0$ requests: $[0, 3, 0]$
- $P_0$'s Need is $[7, 4, 3]$.
  - Step 1: $[0, 3, 0] \le [7, 4, 3]$? **PASSED.**
  - Step 2: $[0, 3, 0] \le [3, 3, 2]$? **PASSED.**
  - Step 3: Tentative Available becomes $[3, 0, 2]$.
  - Step 4: In tentative state, Available Memory is $0$. Every single process in the system needs at least 1 unit of memory to finish. No process can finish! State is **UNSAFE**.
  - Step 5: Request is **DENIED** and rolled back. The potential deadlock was successfully avoided!

---

## 4. Does This Allocate Hardware Resources on Your Real Computer?

**NO.** 

When you request $R_0 = 1$ and the request is granted:
- It alters an integer in the SQLite file `instance/database.db`.
- It recalculates the HTML tables in your browser.
- It does **not** call Windows memory management or CPU affinity APIs.
- Your computer's real hardware RAM and CPU usage remain completely untouched.

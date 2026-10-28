# Operating Systems Algorithms Reference

This document details the mathematical formulation, algorithmic logic, time complexity, and data structures of each Operating Systems algorithm implemented in the **Deadlock-Safe Task Manager**.

---

## 1. Safety Algorithm (Banker's Algorithm Core)

### Objective
Determines whether the system is in a **Safe State** (i.e., there exists at least one order $\langle P_0, P_1, \dots, P_{n-1} \rangle$ in which every process can obtain its maximum demand, finish execution, and release all held resources).

### Algorithm Formulation
1. **Initialize Vectors**:
   $$\text{Work} = \text{Available}$$
   $$\text{Finish}[i] = \text{false} \quad \forall i \in \{0, 1, \dots, n-1\}$$
2. **Find an index $i$** such that:
   $$\text{Finish}[i] == \text{false} \quad \land \quad \text{Need}[i][j] \le \text{Work}[j] \quad (\forall j \in \{0, \dots, m-1\})$$
   If no such $i$ exists, go to Step 4.
3. **Simulate Execution & Resource Reclamation**:
   $$\text{Work} = \text{Work} + \text{Allocation}[i]$$
   $$\text{Finish}[i] = \text{true}$$
   Append $P_i$ to $\text{SafeSequence}$. Repeat Step 2.
4. **Conclusion**:
   If $\text{Finish}[i] == \text{true} \ \forall i$, then the system is in a **Safe State**. Otherwise, the state is **Unsafe**.

### Time Complexity
$O(m \times n^2)$, where $n$ is the number of processes and $m$ is the number of resource types.

---

## 2. Resource-Request Algorithm

### Objective
Decides whether an immediate request $\text{Request}_i$ from process $P_i$ can be safely granted without risking future deadlock.

### Steps
1. **Demand Boundary Check**: If $\text{Request}_i[j] \le \text{Need}_i[j] \ \forall j$, proceed to Step 2. Otherwise, raise an error condition: process has exceeded its declared maximum claim.
2. **Availability Check**: If $\text{Request}_i[j] \le \text{Available}[j] \ \forall j$, proceed to Step 3. Otherwise, $P_i$ must wait until resources become available.
3. **Tentative Allocation**:
   $$\text{Available}' = \text{Available} - \text{Request}_i$$
   $$\text{Allocation}'_i = \text{Allocation}_i + \text{Request}_i$$
   $$\text{Need}'_i = \text{Need}_i - \text{Request}_i$$
4. **Safety Verification**:
   Execute the Safety Algorithm on the tentative system state.
5. **Commit or Rollback**:
   - If the resulting state is **Safe**, the allocation is permanently committed.
   - If the resulting state is **Unsafe**, the tentative allocation is rolled back, the previous safe state is restored, and $P_i$ is placed into a waiting state.

---

## 3. Deadlock Detection Algorithm (Multiple Instances)

### Objective
Detects whether an active deadlock exists in the current system state, using actual current allocations and outstanding pending requests (without requiring processes to declare maximum demand in advance).

### Algorithm Formulation
1. **Initialize**:
   $$\text{Work} = \text{Available}$$
   $$\text{Finish}[i] = \begin{cases} \text{true} & \text{if } \text{Allocation}[i] = \vec{0} \\ \text{false} & \text{otherwise} \end{cases}$$
2. **Find an index $i$** such that:
   $$\text{Finish}[i] == \text{false} \quad \land \quad \text{Request}[i][j] \le \text{Work}[j] \quad (\forall j)$$
   If found:
   $$\text{Work} = \text{Work} + \text{Allocation}[i]$$
   $$\text{Finish}[i] = \text{true}$$
   Repeat Step 2.
3. **Deadlock Assessment**:
   If $\text{Finish}[i] == \text{false}$ for any $i$, then the system is in **Deadlock**, and process $P_i$ is **deadlocked**.

---

## 4. Wait-For Graph (WFG) & Cycle Detection

### Objective
For systems with single or simplified dependencies, a Wait-For Graph represents dependencies solely between processes.
- Directed edge $P_i \to P_j$ exists if $P_i$ requests a resource $R_k$ held by $P_j$.
- Cycles in the Wait-For Graph are detected using Depth-First Search (DFS) with canonical cycle normalization to identify cyclic wait conditions:
  $$P_1 \to P_2 \to \dots \to P_k \to P_1$$

---

## 5. Deadlock Recovery Strategies

1. **Process Termination**:
   - Abort one or more deadlocked processes.
   - All held resources are released to $\text{Available}$, and pending requests are canceled.
   - Re-running deadlock detection confirms whether the deadlock is resolved.
2. **Resource Preemption (Simulation)**:
   - Forcibly reclaim a resource from a victim process and reassign it to a waiting process.
   - Re-evaluates detection to demonstrate whether preemption broken the deadlock.

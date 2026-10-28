# Deadlock Detection Algorithm Guide

## 1. What is a Deadlock?

In an operating system, a **deadlock** is a permanent blocking condition that occurs when a set of concurrent processes are waiting for resources held by each other, such that no process can make progress, finish execution, or release its held resources.

---

## 2. The Four Necessary Coffman Conditions

In 1971, E. G. Coffman Jr. proved that a deadlock can arise **if and only if** all four of the following conditions hold simultaneously:

1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode (only one process can use the resource at any given time).
2. **Hold and Wait**: A process must currently hold at least one resource while waiting to acquire additional resources currently held by other processes.
3. **No Preemption**: Resources cannot be forcibly taken away from a process; they can only be released voluntarily by the process holding them after completing its task.
4. **Circular Wait**: A closed chain of processes exists such that $P_0$ is waiting for a resource held by $P_1$, $P_1$ is waiting for $P_2$, and $P_n$ is waiting for $P_0$.

---

## 3. Avoidance vs. Detection: The Key Difference

| Feature | Deadlock Avoidance (Banker's Algorithm) | Deadlock Detection Algorithm |
| :--- | :--- | :--- |
| **Philosophy** | "Pessimistic / Proactive" | "Optimistic / Reactive" |
| **Prerequisites** | Requires every process to declare its **Maximum Demand** in advance. | Requires **NO** maximum claim knowledge; uses only current active allocations and requests. |
| **When it runs** | Evaluated on every single resource request before granting it. | Runs periodically or on-demand after requests have already occurred. |
| **Result** | Decides whether the system is **SAFE** or **UNSAFE**. | Identifies whether the system is currently **DEADLOCKED** and lists the exact deadlocked processes. |

---

## 4. Multi-Instance Deadlock Detection Algorithm

Implemented in `algorithms/deadlock_detection.py`, this algorithm works for systems where each resource type may have multiple units (e.g., 2 GPUs, 3 Printers).

### Data Structures:
- **Available**: Vector of length $m$ (currently free units).
- **Allocation**: $n \times m$ matrix (units held by each process).
- **Request**: $n \times m$ matrix (units currently requested by each process).
- **Work**: Temporary vector of length $m$.
- **Finish**: Boolean array of length $n$.

### Mathematical Steps:

#### Step 1: Initialize Vectors
$$\text{Work} = \text{Available}$$
$$\text{For } i = 0, 1, \dots, n-1:$$
$$\text{Finish}[i] = \begin{cases} \text{true} & \text{if } \text{Allocation}[i] == \vec{0} \ (\text{holds no resources}) \\ \text{false} & \text{otherwise} \end{cases}$$
*(If a process holds no resources, it cannot be part of a deadlock, so its Finish is set to true immediately).*

#### Step 2: Search for an Unblocked Process
Find an index $i$ such that:
$$\text{Finish}[i] == \text{false} \quad \land \quad \text{Request}[i][j] \le \text{Work}[j] \quad (\forall j)$$
If no such $i$ exists, proceed to **Step 4**.

#### Step 3: Simulate Satisfaction and Reclamation
When candidate $P_i$ is found:
$$\text{Work} = \text{Work} + \text{Allocation}[i]$$
$$\text{Finish}[i] = \text{true}$$
Repeat **Step 2**.

#### Step 4: Deadlock Identification
If $\text{Finish}[i] == \text{false}$ for any process $i$, then the system is in **DEADLOCK**.
The set of deadlocked processes is:
$$\text{DeadlockedProcesses} = \{ P_i \mid \text{Finish}[i] == \text{false} \}$$

---

## 5. Concrete Numerical Example (Two-Process Deadlock)

Consider the predefined scenario `two_process_deadlock`:
- Resources: $R_1$ (Scanner, Total=1), $R_2$ (Printer, Total=1).
- Processes: $P_1, P_2$.
- Available: $\text{Available} = [R_1: 0, R_2: 0]$.

### Allocation Matrix:
- $P_1$ holds $R_1$: $\text{Allocation}[P_1] = [1, 0]$
- $P_2$ holds $R_2$: $\text{Allocation}[P_2] = [0, 1]$

### Active Request Matrix:
- $P_1$ requests $R_2$: $\text{Request}[P_1] = [0, 1]$
- $P_2$ requests $R_1$: $\text{Request}[P_2] = [1, 0]$

### Algorithm Execution:
1. **Initialize**:
   - $\text{Work} = [0, 0]$
   - Both processes hold allocations, so: $\text{Finish}[P_1] = \text{false}, \text{Finish}[P_2] = \text{false}$.
2. **Evaluate $P_1$**:
   - $\text{Request}[P_1] = [0, 1]$.
   - Is $[0, 1] \le \text{Work}[0, 0]$? **NO** ($1 > 0$ for $R_2$). $P_1$ cannot proceed.
3. **Evaluate $P_2$**:
   - $\text{Request}[P_2] = [1, 0]$.
   - Is $[1, 0] \le \text{Work}[0, 0]$? **NO** ($1 > 0$ for $R_1$). $P_2$ cannot proceed.
4. **Conclusion**:
   - Neither process can make progress.
   - $\text{Finish} = [P_1: \text{false}, P_2: \text{false}]$.
   - **DEADLOCK DETECTED! Deadlocked processes: $\{ P_1, P_2 \}$.**

---

## 6. How the Current Application Executes Detection

1. **User Action**: The user clicks **RUN DEADLOCK DETECTION** on `/deadlock-detection`.
2. **Backend**: Flask invokes `POST /api/deadlock-detection`, which runs `DeadlockDetectionAlgorithm.run()`.
3. **State Updates**:
   - The processes identified as deadlocked have their `state` in the SQLite database updated to `DEADLOCKED`.
   - An audit log entry `DEADLOCK_DETECTION` is created.
4. **UI Response**:
   - A pulsing red alert banner appears: **DEADLOCK DETECTED! Deadlocked: P1, P2**.
   - The **Deadlock Recovery Panel** unlocks immediately, giving the user options to terminate a victim process or simulate preemption.
   - The execution trace shows why each process was blocked and the resource deficit that prevented it from finishing.

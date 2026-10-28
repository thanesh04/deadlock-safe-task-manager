# Deadlock Recovery Strategies

## 1. Why is Deadlock Recovery Required?

In an operating system that uses **Deadlock Detection** (rather than avoidance), processes are allowed to acquire resources freely without declaring maximum claims. Consequently, a circular wait deadlock may occur at runtime.

Once a deadlock is detected by the operating system, it will **not** fix itself. The participating processes are frozen indefinitely. The operating system must take active intervention to break the circular wait and restore throughput.

---

## 2. Recovery Strategies Implemented in the Application

The application implements the two primary classical operating systems recovery strategies:
1. **Process Termination** (Single victim or All deadlocked processes).
2. **Resource Preemption (Educational Simulation)**.

These are implemented in `algorithms/recovery.py` and accessible on the **Deadlock Detection** screen (`/deadlock-detection`).

---

## 3. Strategy 1: Process Termination

### How it works:
The operating system selects one or more deadlocked processes as "victims" and aborts them.

### What happens in the application:
When you select victim process $P_1$ and click **Terminate Victim**:
1. The backend method `Simulator.recover_deadlock('terminate', {'pids': ['P1']})` is called.
2. In the SQLite database:
   - For every resource allocated to $P_1$, its allocated count is saved and then set to `0`:
     $$\text{Allocation}[P_1][R_j] = 0$$
   - The system `Available` vector is incremented by the released amounts:
     $$\text{Available}[R_j] = \text{Available}[R_j] + \text{Released}[R_j]$$
   - $P_1$'s `state` is set to `TERMINATED`.
   - Any pending requests from $P_1$ are marked as `CANCELLED`.
   - An audit log entry `DEADLOCK_RECOVERY` is generated.
3. The application **automatically re-runs the Deadlock Detection Algorithm** on the remaining active processes.
4. If the reclaimed resources allow the remaining processes to satisfy their requests, the banner immediately updates to **DEADLOCK RESOLVED!**

> **CRITICAL REMINDER**: Terminating $P_1$ terminates the **simulated Python/SQLite object** representing process $P_1$. It does **NOT** kill any real Windows programs or processes running on your computer.

---

## 4. Strategy 2: Simulated Resource Preemption

### How it works:
Instead of killing an entire process (which loses all computation work done so far), the operating system forcibly seizes a resource from a holding process (the victim) and reallocates it to a waiting process (the target).

### Why it is labeled a Simulation:
In a real production kernel, resource preemption is exceptionally complex: it requires **checkpointing** and **rollback** mechanisms so the victim can later resume from a consistent saved state without data corruption. 

In this educational project, preemption is clearly marked as an **educational simulation**:
- The code tests the effect of transferring 1 unit of a resource from a holding process to a blocked process:
  $$\text{Allocation}[P_{\text{victim}}][R_k] = \text{Allocation}[P_{\text{victim}}][R_k] - 1$$
  $$\text{Allocation}[P_{\text{target}}][R_k] = \text{Allocation}[P_{\text{target}}][R_k] + 1$$
  $$\text{Request}[P_{\text{target}}][R_k] = \text{Request}[P_{\text{target}}][R_k] - 1$$
- It re-evaluates the Deadlock Detection algorithm to show students whether transferring that specific resource successfully breaks the circular wait cycle.

---

## 5. Summary of Mathematical State Changes During Recovery

| Vector / Matrix | Before Recovery (Deadlocked) | After Terminating $P_1$ (Holding 1 unit of $R_1$) |
| :--- | :--- | :--- |
| **$P_1$ Allocation** | $\text{Allocation}[P_1][R_1] = 1$ | $\text{Allocation}[P_1][R_1] = 0$ |
| **Available $R_1$** | $\text{Available}[R_1] = 0$ | $\text{Available}[R_1] = 1$ (reclaimed) |
| **$P_2$ Request** | $P_2$ requests 1 unit of $R_1$ (blocked) | $P_2$ request can now be satisfied by Available $R_1$ |
| **Finish Vector** | $\text{Finish} = [P_1: F, P_2: F]$ | $\text{Finish} = [P_2: T]$ (All active processes finished) |
| **Deadlock Status** | **DEADLOCK DETECTED** | **NO DEADLOCK / RESOLVED** |

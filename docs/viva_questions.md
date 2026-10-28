# 35 Viva Examination Questions & Answers

This document prepares you for any theoretical, technical, or implementation questions an examiner might ask during your Operating Systems lab viva or project evaluation.

---

### Q1: What is a Deadlock?
**Answer**: A deadlock is a permanent blocking situation where a set of concurrent processes are waiting for resources held by one another, such that no process can make progress, finish its execution, or release its held resources.

---

### Q2: What are the Four Necessary Coffman Conditions for Deadlock?
**Answer**: A deadlock can occur if and only if these four conditions hold simultaneously:
1. **Mutual Exclusion**: At least one resource must be held in a non-shareable mode.
2. **Hold and Wait**: A process holds at least one resource and is waiting to acquire additional resources held by other processes.
3. **No Preemption**: Resources cannot be forcibly seized; only released voluntarily after a process finishes.
4. **Circular Wait**: A closed chain of processes exists such that $P_0$ waits for $P_1$, $P_1$ waits for $P_2$, and $P_n$ waits for $P_0$.

---

### Q3: What is the Banker's Algorithm?
**Answer**: Developed by Edsger Dijkstra, Banker's Algorithm is a **deadlock avoidance** algorithm. It simulates resource allocation for pre-declared maximum claims and only commits a request if the resulting system state is guaranteed to be a **Safe State** where all processes can eventually complete.

---

### Q4: Why is Banker's Algorithm called an "Avoidance" Algorithm?
**Answer**: Because it acts *proactively*. Before granting any resource request, it evaluates whether granting the request could transition the system into an unsafe state where deadlock might happen in the future. If unsafe, the allocation is denied or delayed to **avoid** entering the deadlock zone.

---

### Q5: What is a Safe State?
**Answer**: A state is safe if the operating system can allocate resources to each process (up to its declared maximum) in some order without encountering a deadlock. Formally, a state is safe if there exists at least one **Safe Sequence**.

---

### Q6: What is an Unsafe State? Does an Unsafe State Mean Deadlock Has Occurred?
**Answer**: An unsafe state is **not** necessarily a deadlock. It simply means the OS can no longer *guarantee* that deadlock will not happen if all processes demand their remaining maximum needs simultaneously. Deadlocks are a strict subset of unsafe states.

---

### Q7: What is a Safe Sequence?
**Answer**: A sequence of processes $\langle P_1, P_3, P_0, P_2, P_4 \rangle$ such that for each process $P_i$, its remaining Need can be satisfied by the currently Available resources plus the resources already held by all processes preceding it in the sequence.

---

### Q8: What is the Remaining Need Vector?
**Answer**: It represents the remaining instances of each resource that a process may request before completing its task.

---

### Q9: Why is $\text{Need} = \text{Maximum} - \text{Allocation}$?
**Answer**: Because a process's declared Maximum represents its total lifetime demand. The remaining need is therefore whatever part of that maximum has not yet been allocated to it. Storing it independently could lead to data inconsistency, so our application computes it dynamically.

---

### Q10: What is the Available Vector?
**Answer**: A 1D vector of length $m$ representing the number of unallocated units of each resource type currently free in the system resource pool:
$$\text{Available}[j] = \text{Total}[j] - \sum_{i} \text{Allocation}[i][j]$$

---

### Q11: What is the Allocation Matrix?
**Answer**: A 2D matrix of size $n \times m$ where $\text{Allocation}[i][j]$ specifies the number of instances of resource type $R_j$ currently held by process $P_i$.

---

### Q12: What is the Difference Between Deadlock Avoidance and Deadlock Detection?
**Answer**: 
- **Avoidance (Banker's Algorithm)**: Requires *a priori* maximum claims. Runs *before* allocation. Guarantees the system never enters an unsafe state.
- **Detection**: Does *not* require maximum claims. Runs *after* requests are made. Scans current allocations and active requests to find existing blocked processes.

---

### Q13: What is a Resource Allocation Graph (RAG)?
**Answer**: A directed bipartite graph where nodes are either Processes (circles) or Resources (rectangles). Directed edge $R_j \to P_i$ denotes allocation (held resource), and $P_i \to R_j$ denotes request (waiting).

---

### Q14: What is a Wait-For Graph (WFG)?
**Answer**: A simplified graph derived by removing resource nodes from a RAG. Nodes are processes only. Directed edge $P_i \to P_j$ means process $P_i$ is waiting for a resource currently held by $P_j$.

---

### Q15: What Does a Cycle in a Graph Mean?
**Answer**: A cycle represents a circular wait condition ($P_1 \to P_2 \to P_1$). In single-unit resource systems, a cycle is a necessary and sufficient condition for deadlock. In multi-unit systems, a cycle is necessary but may not always be sufficient unless all instances are tied up in the cycle.

---

### Q16: Are $P_0$–$P_4$ in This Project Real Windows Processes?
**Answer**: **NO.** They are simulated Python/database objects stored in our SQLite database. They represent textbook tasks (Web Server, Database Worker, etc.) designed for educational simulation.

---

### Q17: Are $R_0$–$R_2$ Real Hardware Resources?
**Answer**: **NO.** They are logical counters in our database. $R_0 = 10$ represents 10 simulated CPU cores, not physical hardware cores on our laptop motherboard.

---

### Q18: What Happens When $P_1$ Requests a Resource in the App?
**Answer**: The 5-step Resource-Request Algorithm runs: checks $Request \le Need$, checks $Request \le Available$, simulates a tentative state in memory, tests the state using the Safety Algorithm, and commits the allocation to the database only if safe.

---

### Q19: What Happens When a Request is Denied?
**Answer**: The tentative state is rolled back. The database remains in its prior safe state, the process state is set to `WAITING`, and an audit event `REQUEST_DENIED` is logged.

---

### Q20: What Happens When a Process Releases Resources?
**Answer**: Its allocated counter in the database is decremented, the system's `Available` vector is incremented, its remaining `Need` increases, and an audit event `RESOURCE_RELEASED` is logged.

---

### Q21: What Happens When a Simulated Process is Terminated?
**Answer**: Its state becomes `TERMINATED`, all resources it currently held are reclaimed and returned to `Available`, its pending requests are cancelled, and deadlock detection is re-run.

---

### Q22: Can This Application Kill or Crash a Real Windows Process?
**Answer**: **NO.** The project only modifies records in `instance/database.db`. It never calls native OS process management APIs (`TerminateProcess` or `kill`).

---

### Q23: Does Requesting "Memory (GB)" Actually Consume RAM on the PC?
**Answer**: **NO.** It simply decrements an integer in the database. Physical RAM utilization on the host machine is completely unaffected.

---

### Q24: What is `psutil`?
**Answer**: `psutil` (Python System and Process Utilities) is a cross-platform Python library used to query hardware utilization, memory usage, CPU percentages, and running process lists directly from the host operating system kernel.

---

### Q25: Which Data on the Monitor Page (`/monitor`) is Real?
**Answer**: All of it. The CPU percentage, physical RAM in gigabytes, swap space, and total Windows process count (e.g., 230 processes) on `/monitor` are live, real measurements queried via `psutil`.

---

### Q26: Does `psutil` Feed Data into Banker's Algorithm?
**Answer**: **NO.** There is a strict architectural firewall between the two. Real host telemetry is purely for monitoring and is never used as input to the simulated deadlock matrices.

---

### Q27: What is a Predefined Scenario?
**Answer**: A curated JSON configuration that presets processes, resources, maximum claims, allocations, and requests to reliably demonstrate textbook OS states (such as safe states, unsafe states, or circular deadlocks).

---

### Q28: Why Did You Implement Predefined Scenarios?
**Answer**: To make the project fast and reliable to demonstrate during exams and viva presentations without risking manual typing errors during live matrix entry.

---

### Q29: Why Did You Use SQLite?
**Answer**: SQLite is lightweight, serverless, zero-configuration, and runs entirely within the project directory (`instance/database.db`), making the project completely portable across any student or teacher machine.

---

### Q30: Why Did You Choose Flask for the Backend?
**Answer**: Flask is a lightweight Python web micro-framework that allows a clean separation of concerns: REST API routes in `routes/api.py`, independent algorithm modules in `algorithms/`, and simulation management in `simulation/`.

---

### Q31: Why Did You Use Cytoscape.js for Graphs?
**Answer**: Cytoscape.js is a high-performance, industry-standard graph theory and network analysis library that supports interactive zooming, panning, force-directed layouts, and programmatic node/edge styling to highlight deadlock cycles.

---

### Q32: What is the Fundamental Difference Between Simulation and Monitoring?
**Answer**: 
- **Simulation**: Modeling theoretical concepts (Banker's Algorithm, RAG, WFG) in a controlled mathematical environment where parameters can be manipulated at will.
- **Monitoring**: Read-only passive observation of real physical computer hardware without altering its internal logic.

---

### Q33: What is Deadlock Recovery?
**Answer**: The operational techniques used by an operating system to break a detected circular wait and restore system progress—primarily through **process termination** or **resource preemption**.

---

### Q34: What is Resource Preemption?
**Answer**: Forcibly taking an allocated resource away from one holding process (the victim) and giving it to another process waiting for it. In real OSs, this requires complex checkpointing and rollback mechanisms.

---

### Q35: What is the Main Limitation of Banker's Algorithm in Real-World Operating Systems?
**Answer**: Banker's Algorithm requires every process to know and declare its **Maximum Resource Demand in advance**, which is almost impossible for general-purpose user software (like web browsers or IDEs). Therefore, modern desktop OSs typically rely on detection, thread timeouts, or physical resource over-provisioning rather than strict Banker's avoidance.

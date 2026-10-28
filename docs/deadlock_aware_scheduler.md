# Deadlock-Aware CPU Scheduler & Process Behavior Anomaly Detector

### Advanced Dynamic Task Scheduling, Banker's Safe Admission, and Dynamic Aging

---

## 1. Academic Motivation & Novelty

### The Faculty Review Problem
Traditional academic simulators suffer from a major design flaw:
1. They either simulate **CPU Scheduling** (FCFS, SJF, Round Robin, Priority) with static burst times and **zero resource dependencies**.
2. Or they simulate **Deadlock Avoidance** (Banker's Algorithm) as **static matrix arithmetic without an actual CPU dispatch loop or execution time**.

In a real operating system kernel, the **CPU Dispatcher** and the **Resource Manager** operate continuously in tandem:
- A task cannot run on a CPU core if its next instruction requires a resource whose acquisition would lead the operating system into an **unsafe state**.
- If Banker's Algorithm denies an allocation, the OS kernel must not freeze the CPU; it must **context-switch** immediately to another viable task in the Ready Queue.
- Conversely, Banker's Algorithm has a known theoretical drawback: **Process Starvation**. A process requiring large resource allocations can wait indefinitely if smaller requests keep being granted.

The **Deadlock-Aware CPU Scheduler** solves these challenges by combining **dynamic CPU scheduling**, **real-time Banker's safety checks**, **dynamic priority aging**, and **behavioral anomaly detection** into a single interactive simulator.

---

## 2. Core Architecture: The Coordinated Execution Loop

Every discrete clock tick ($T \to T + 1$) advances through this pipeline:

```text
               +-------------------------------------------+
               | Clock Tick T: Check Newly Arrived Tasks   |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               | Ready Queue Evaluation (RR / SRTF / Prio) |
               +-------------------------------------------+
                                     |
                                     v
               +-------------------------------------------+
               | Does Candidate Process Request Resources? |
               +-------------------------------------------+
                        /                         \
                 YES   /                           \   NO
                      v                             v
       +-------------------------------+    +------------------------+
       | Mode: DEADLOCK_AWARE vs NAIVE |    | Dispatch directly      |
       +-------------------------------+    | to CPU Core            |
             /                   \          +------------------------+
      AWARE /                     \ NAIVE                |
           v                       v                     |
+---------------------+   +---------------------+        |
| Run Banker's Safety |   | Blind Allocation    |        |
| on Tentative State  |   | (May cause cycle!)  |        |
+---------------------+   +---------------------+        |
     /             \                 |                   |
SAFE/       UNSAFE  \                v                   |
   v                 v     +--------------------+        |
+----------+ +-----------+ | WFG Cycle Detect:  |        |
| Grant    | | INTERCEPT!| | Flag DEADLOCKED    |        |
| Resource | | Suspend   | +--------------------+        |
| & Run    | | to Wait   |                               |
+----------+ +-----------+                               |
     |             |                                     |
     |             v                                     |
     |       +------------------------------------+      |
     |       | Starvation Ticks +1                |      |
     |       | If >= Threshold -> AGING (+1 Prio) |      |
     |       | Context Switch to Next Task        |      |
     |       +------------------------------------+      |
     |                                                   |
     +-----------------------+---------------------------+
                             |
                             v
               +-------------------------------------------+
               | Execute Burst Tick & Update Gantt Chart   |
               +-------------------------------------------+
```

---

## 3. Four Supported CPU Scheduling Policies

1. **Round Robin (RR)**:
   - Configurable time quantum ($q = 1, 2, 3 \dots$).
   - When a process exhausts its quantum slice, it is preempted to the tail of the Ready Queue and the next ready task is dispatched.
2. **Shortest Remaining Time First (SRTF / Preemptive SJF)**:
   - Dispatches the task with the smallest remaining CPU burst time.
   - Minimizes theoretical average waiting time across the workload.
3. **Preemptive Priority Scheduling**:
   - Dispatches the task with the highest priority (lower numeric value = higher priority).
   - Seamlessly reflects **Dynamic Aging** boosts in real time.
4. **First-Come, First-Served (FCFS)**:
   - Dispatches tasks strictly in arrival order.

---

## 4. Anomaly Detection & Starvation Defense

### A. The Greed Index
Calculates what percentage of total system capacity a process declares in its maximum claim:
$$\text{Greed Index} = \frac{\sum_{r \in R} \text{MaxClaim}[P_i][r]}{\sum_{r \in R} \text{TotalCapacity}[r]} \times 100\%$$
- **$\ge 65\%$**: Flagged as a **High Resource Greed** anomaly. The process is monitored closely because granting its requests early can severely restrict system safety.

### B. Dynamic Aging & Starvation Defense
- **The Problem**: If process $P_2$ requests multiple resource instances, Banker's Algorithm might repeatedly find the system unsafe while admitting lighter tasks ($P_1, P_3$). Without defense, $P_2$ starves.
- **The Solution**: Every tick a task remains in `SAFETY_WAIT`, its `starvation_ticks` counter increments.
- When `starvation_ticks >= 3` (aging threshold), the engine applies an **Aging Boost** ($\text{Effective Priority} = \text{Base Priority} - \text{Boost}$).
- In Priority mode, this elevates the starving process to the head of the dispatch queue, guaranteeing it first access to newly reclaimed resources.

---

## 5. Comparative Showdown: Deadlock-Aware vs. Naive Mode

To prove the necessity of Banker's Algorithm during viva demonstrations, the scheduler includes a live **Mode Toggle**:

| Dimension | Naive Mode (No Protection) | Deadlock-Aware Mode (Banker's Protected) |
| :--- | :--- | :--- |
| **Allocation Policy** | Grants resources immediately if $Req \le Available$. | Simulates tentative state and runs Safety Algorithm first. |
| **Circular Wait Contention** | Allowed to form freely. | Intercepted and blocked before the circular wait occurs. |
| **Gantt Chart Behavior** | Stalls in **RED (`DEADLOCKED`)** when a cycle occurs. | Intercepted task goes to **ORANGE (`SAFETY_WAIT`)**; CPU context-switches to safe tasks. |
| **Final Outcome** | Permanent deadlock freeze. | 100% completion of all tasks with zero system hangs. |

---

## 6. Viva Spoken Script: How to Present the Scheduler to Faculty

> **What to Say to the Examiner:**
> 
> *"Sir/Madam, in our first review, the faculty noted that our project primarily demonstrated textbook Banker's algorithm matrices. To introduce true novelty and bridge the gap with real operating systems, we built the **Deadlock-Aware CPU Scheduler**.*
> 
> *In this new module (`/scheduler`), processes are not static matrix rows. They are dynamic execution programs with arrival times, CPU burst cycles, and scheduled resource acquisitions.*
> 
> *Let me demonstrate our **Deadlock Showdown** scenario:*
> 
> 1. *First, I set the mode to **Naive**. When I click Play, processes $P_0$ and $P_1$ execute until tick $T=4$. Notice how the Gantt chart suddenly freezes in RED: $P_0$ holds $R_0$ waiting for $R_1$, while $P_1$ holds $R_1$ waiting for $R_0$. Our Wait-For Graph engine detects the cycle and flags the system as DEADLOCKED.*
> 
> 2. *Now, I click Reset and switch the mode to **Deadlock-Aware (Banker's)**. When I run the exact same workload, look at tick $T=4$: Banker's algorithm intercepts $P_1$'s unsafe request! It blocks $P_1$ from creating the circular wait, context-switches the CPU to $P_2$, allows $P_0$ to complete and release its resources, and then safely finishes $P_1$.*
> 
> 3. *Furthermore, we implemented **Dynamic Aging**: if a process waits longer than 3 ticks due to safety constraints, the kernel elevates its priority to prevent indefinite starvation.*
> 
> *This directly models how real kernels balance CPU throughput, task latency, and deadlock avoidance."*

---

## 7. Model Viva Questions & Answers

### Q1: Why do commercial OS kernels (Windows / Linux) not use Banker's algorithm in their CPU schedulers?
**Answer**: Banker's Algorithm requires processes to declare their **maximum resource demand in advance**, and assumes the total number of resource instances is fixed. In general-purpose OSs like Windows or Linux, applications dynamically allocate memory and file handles unpredictably. However, Banker's-style schedulers are used in **hard real-time systems**, embedded mission-critical controllers, and avionics where tasks are deterministic.

### Q2: What happens to CPU utilization when Banker's Algorithm intercepts an unsafe request?
**Answer**: In a naive single-task system, an intercepted request could stall the CPU. In our Deadlock-Aware Scheduler, the dispatcher performs an immediate **context switch** to the next viable process in the Ready Queue, keeping CPU utilization high while guaranteeing zero deadlocks.

### Q3: How does your dynamic aging avoid starvation without causing deadlocks?
**Answer**: Aging boosts the task's scheduling priority, ensuring that as soon as any active process terminates and returns resources to the `Available` pool, the starving task is evaluated first for safe admission before newer, lower-priority tasks can claim them.

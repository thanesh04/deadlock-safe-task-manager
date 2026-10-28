# CPU & Task Scheduler: Comprehensive Demonstration Guide & Technical Reference

### Word-for-Word Spoken Viva Script and Complete Technical Breakdown

---

## 1. What is the CPU & Task Scheduler?

The **CPU & Task Scheduler** is an advanced, real-time operating systems execution simulator that bridges **CPU Process Scheduling** and **Deadlock Management**.

### The Conceptual Gap it Solves:
- Traditional Task Managers (like Windows Task Manager or Linux `top`) only display passive CPU percentages and process lists. They do not reveal the algorithmic mechanics of how tasks acquire contested hardware locks or avoid system freezes.
- Traditional academic Banker's algorithm calculators are **static matrix worksheets**. They evaluate numbers in tables, but there is no clock, no CPU core, no dispatching, and no concept of elapsed time.

The **CPU & Task Scheduler** simulates a living OS kernel:
1. Every discrete clock tick ($T = 0, 1, 2, \dots$), a hardware timer interrupt fires.
2. The **CPU Dispatcher** picks a candidate process from the Ready Queue according to a scheduling algorithm (Round Robin, SRTF, Priority, FCFS).
3. As the process executes its burst instructions on the CPU, it reaches milestone ticks where it requests contested system resources ($R_0, R_1, R_2$).
4. The **Resource Guard** intercepts the request and runs Dijkstra's Banker's Algorithm in real time.
5. If granting the resource leaves the system in an **Unsafe State**, the task is immediately suspended to a `SAFETY_WAIT` queue, and the CPU instantly **context-switches** to the next safe process—preventing CPU idle waste while maintaining zero deadlocks.

---

## 2. Technical Component Breakdown

### A. Workload Scenarios
The simulator provides 4 curated workloads representing classic operating system situations:

1. **Balanced Multi-Process (4 Tasks, 3 Resources)**:
   - Mix of high-priority I/O tasks and long CPU-burst compute tasks.
   - Demonstrates smooth Round Robin interleaving, interleaved resource acquisition, voluntary release, and optimal CPU throughput.
2. **Deadlock Showdown (Circular Contention)**:
   - Two competing transaction workers ($P_0$ and $P_1$) that request opposite mutex locks ($R_0$ and $R_1$) during execution, alongside an independent background worker ($P_2$).
   - Designed specifically to contrast **Naive Mode** (which crashes into a circular deadlock) against **Deadlock-Aware Mode** (which averts the deadlock cleanly).
3. **Starvation & Dynamic Aging Demo**:
   - Contains a "Greedy Batch Task" demanding large fractions of system RAM and CPU cores, alongside quick, lightweight API tasks.
   - Demonstrates the famous flaw of Banker's Algorithm (starvation of heavy tasks) and how the **Dynamic Aging Engine** rescues the starving process by elevating its priority.
4. **Load From Current Database State**:
   - Reads the active processes and multi-instance resources configured in the main SQLite database (`/processes` and `/resources`).
   - Automatically computes realistic CPU burst times and converts current matrix demands into milestone scheduling events.

---

### B. Scheduling Policies

1. **Round Robin (RR)**:
   - Preemptive time-sliced dispatching.
   - Tasks execute for at most $q$ clock ticks before being rotated to the tail of the Ready Queue.
   - Guarantees fair CPU sharing and low response time for interactive workloads.
2. **Shortest Remaining Time First (SRTF / Preemptive SJF)**:
   - Dispatches the task with the smallest remaining CPU burst time ($t_{\text{remaining}}$).
   - If a newly arrived process has a shorter burst time than the currently executing process, the CPU preempts the current process immediately.
   - Mathematically minimizes average waiting time across all tasks.
3. **Preemptive Priority Scheduling**:
   - Dispatches the task with the highest priority (convention: lower integer value = higher priority, e.g., Priority 1 beats Priority 4).
   - Dynamically reflects **Aging Boosts** in real time: as a starving process earns priority boosts, it jumps ahead in the Ready Queue.
4. **First-Come, First-Served (FCFS)**:
   - Non-preemptive scheduling strictly based on arrival timestamps.
   - Serves as the classic academic baseline to demonstrate the convoy effect.

---

### C. Time Quantum ($q$)
- **Definition**: The fixed slice of continuous CPU execution granted to a process under Round Robin before preemption occurs.
- **Configurable Range**: 1 to 10 ticks.
- **Operating Systems Tradeoff**:
  - **Small Quantum ($q = 1$)**: High responsiveness and fine-grained interleaving, but increases **Context Switch overhead**.
  - **Large Quantum ($q \ge 6$)**: Degenerates toward FCFS, increasing waiting time for short interactive tasks.
  - **Optimal Textbook Setting ($q = 2$)**: Perfectly balances responsive time-slicing with minimal context switching.

---

### D. The Resource Guard (Modes of Operation)

| Parameter | 🛡️ Deadlock-Aware Mode | ⚠️ Naive Mode |
| :--- | :--- | :--- |
| **Safety Engine** | Dijkstra's Banker's Algorithm (`algorithms/bankers.py`). | Simple capacity check ($Req \le Available$). |
| **Decision Flow** | Computes tentative $\text{Work}$ and $\text{Finish}$ vectors. If no safe sequence exists, request is **INTERCEPTED**. | Grants resources blindly as long as inventory $> 0$. |
| **On Unsafe Condition** | Process is suspended to `SAFETY_WAIT`. Scheduler performs immediate **Context Switch** to another task. | Process acquires resource, creating an invisible circular wait hazard. |
| **Deadlock Handling** | **Avoidance**: Deadlocks are prevented from ever forming ($0\%$ system downtime). | **Stall**: Circular wait freezes the system. Wait-For Graph flags tasks in **RED (`DEADLOCKED`)**. |

---

### E. Process Execution & Behavioral Anomaly Matrix

The live table tracks each process across 8 real-time dimensions:

1. **PID & Name**: Unique process identifier ($P_0, P_1, \dots$) and descriptive service name.
2. **Lifecycle State**:
   - `READY`: In Ready Queue, waiting for CPU dispatch.
   - `RUNNING`: Currently occupying the CPU core and executing instructions.
   - `SAFETY_WAIT`: Intercepted by Banker's Algorithm; waiting for other tasks to release resources before safe admission.
   - `DEADLOCKED`: Trapped in an unresolvable circular wait (Naive mode only).
   - `TERMINATED`: Burst completed; all held resources returned to system pool.
3. **Burst Progress Bar**:
   - Displays executed ticks over total burst ($t_{\text{progress}} / t_{\text{burst}}$) and completion percentage ($0\% \to 100\%$).
4. **Priority (with Aging Boost)**:
   - Displays base priority ($P_1, P_2, \dots$) and highlights dynamic promotions: `+1 Boost`, `+2 Boost`.
5. **Held Resources**:
   - Live tally of allocated physical tokens, e.g. `CPU_Core:1, Memory_GB:2`.
6. **Starvation Ticks Counter**:
   - Counts consecutive cycles a process has been denied resources by the safety algorithm.
   - Resets to 0 once the process is safely admitted and executing on the CPU.
7. **Greed Index**:
   - Calculates the ratio of the process's maximum declared claims to total system inventory:
     $$\text{Greed Index} = \frac{\sum \text{MaxClaim}[P_i]}{\sum \text{TotalCapacity}} \times 100\%$$
8. **Behavioral Status & Risk Badges**:
   - 🟢 `Normal`: Standard execution patterns.
   - 🟡 `Resource Hoarder`: Holding allocated resources while blocked or waiting.
   - 🟠 `Starvation Risk`: Denied resources for $\ge 3$ consecutive cycles.
   - 🔴 `Critical Risk`: High greed combined with prolonged starvation.

---

### F. Performance Metrics Explained

1. **CPU Utilization %**:
   $$\text{CPU Utilization} = \frac{\text{Active Execution Ticks (Non-Idle)}}{\text{Total Clock Ticks}} \times 100\%$$
   *Measures the efficiency of the dispatcher. A high percentage proves that the scheduler successfully finds alternate tasks when one task is safety-blocked.*
2. **Average Turnaround Time**:
   $$\text{Turnaround Time} = T_{\text{completion}} - T_{\text{arrival}}$$
   $$\text{Average Turnaround} = \frac{\sum_{i=1}^{N} \text{Turnaround}(P_i)}{N}$$
   *Measures the total latency from the moment a job arrives in the system until it completely finishes and releases all resources.*
3. **Average Waiting Time**:
   $$\text{Waiting Time} = \text{Turnaround Time} - \text{Burst Time}$$
   $$\text{Average Waiting} = \frac{\sum_{i=1}^{N} \text{Waiting}(P_i)}{N}$$
   *Measures how long processes spent idling in Ready or Safety Wait queues.*
4. **Context Switches Count**:
   *The number of times the CPU saved execution state and dispatched a different process. Tracks scheduling overhead.*
5. **Deadlocks Averted**:
   *The exact count of resource requests that were mathematically unsafe and were intercepted by Banker's Algorithm before a circular wait could form.*

---

## 3. Word-for-Word Spoken Viva Demonstration Script

Use this exact script when presenting the CPU & Task Scheduler to your teacher or examiner.

---

### ACT 1: Introducing the Feature (1 Minute)

> **What to Say:**
> *"Good morning, Sir/Madam. In response to our initial review, where the faculty suggested extending the project beyond static Banker's algorithm matrices, we designed and built the **Deadlock-Aware CPU Scheduler**.*
> 
> *In a real operating system kernel, resource allocation does not happen in isolation. It happens while the CPU is actively dispatching tasks across clock cycles.*
> 
> *Here on the `/scheduler` screen, our processes are no longer just rows in a matrix. They are dynamic programs with arrival times, CPU burst cycles, priorities, and runtime resource milestones. We have integrated 4 classic CPU scheduling algorithms with real-time Banker's avoidance, Dynamic Priority Aging, and Behavioral Anomaly Detection."*

---

### ACT 2: Demonstrating the "Deadlock Showdown" (2 Minutes)

> **Action**:
> 1. In the **Workload Scenario** dropdown, select **"Deadlock Showdown (Circular Contention)"**.
> 2. Ensure **Resource Guard** is set to **"⚠️ Naive (No Safety Intercept)"**.
> 3. Click **Play** (or click **Step (+1)** 5 times).

> **What to Say:**
> *"To prove the necessity of Banker's Algorithm, let us first run the system under **Naive Mode**—which is how standard multi-threaded programs behave without OS deadlock avoidance.*
> 
> *In this scenario, task $P_0$ needs Mutex A then Mutex B. Task $P_1$ needs Mutex B then Mutex A.*
> 
> *Notice what happens as the clock reaches $T=4$:*
> - *$P_0$ acquired Mutex A and is waiting for Mutex B.*
> - *$P_1$ acquired Mutex B and is waiting for Mutex A.*
> - *Neither can proceed. Our Wait-For Graph engine detects the cycle $\langle P_0 \to P_1 \to P_0 \rangle$, and the Gantt chart freezes in **RED (DEADLOCKED)**.*
> - *The CPU becomes completely stalled, and no further progress can be made."*

---

### ACT 3: The Banker's Avoidance Intervention (2 Minutes)

> **Action**:
> 1. Click **Reset**.
> 2. Switch **Resource Guard** to **"🛡️ Deadlock-Aware (Banker's)"**.
> 3. Click **Play** (or step through using **Step (+1)**).

> **What to Say:**
> *"Now, let us run the exact same workload under our **Deadlock-Aware Scheduler**.*
> 
> *Watch tick $T=4$ very carefully:*
> - *When $P_1$ requests Mutex B, the scheduler queries Dijkstra's Banker's Algorithm.*
> - *The engine simulates the tentative allocation and detects that the state would become **Unsafe** because neither process could guarantee completion.*
> - *Instead of granting the lock and freezing the system, Banker's **intercepts** the request!*
> - *Notice how the Gantt chart tags $P_1$ in orange as `SAFETY_WAIT`.*
> - *Crucially, the CPU does not freeze: the dispatcher performs an immediate **Context Switch** to $P_2$ (an independent task) and then to $P_0$.*
> - *$P_0$ finishes its burst, terminates, and returns Mutex A to the available pool.*
> - *Now that the state is safe, $P_1$ is awakened, acquires its resources, and completes!*
> 
> *All tasks successfully finish with **0 deadlocks** and **100% completion**."*

---

### ACT 4: Dynamic Aging & Starvation Defense (1.5 Minutes)

> **Action**:
> 1. Switch **Workload Scenario** to **"Starvation & Aging Demo"**.
> 2. Select **Scheduling Policy** as **"Preemptive Priority"**.
> 3. Click **Play**.

> **What to Say:**
> *"A well-known academic criticism of Banker's Algorithm is **Process Starvation**: a process demanding large resources can be repeatedly bypassed if smaller processes keep claiming resources.*
> 
> *To solve this, we implemented **Dynamic Priority Aging**:*
> - *Notice Task $P_0$ (Batch Analytics). It has a high Greed Index of 70% and lower priority.*
> - *As smaller tasks ($P_1, P_2$) get admitted, $P_0$'s Starvation Counter ticks up in the table: 1, 2, 3 cycles.*
> - *As soon as it hits the aging threshold of 3 ticks, our Dynamic Aging engine fires: it awards $P_0$ an **Aging Boost (+1 Priority)**, raising its effective priority.*
> - *This elevates $P_0$ to the front of the ready queue, reserving newly released resources and allowing it to finish.*
> - *This demonstrates how an advanced operating system kernel balances deadlock avoidance with fairness."*

---

### ACT 5: Explaining Performance Metrics & Wrapping Up (1 Minute)

> **Action**: Point to the bottom KPI cards and the live log feed.

> **What to Say:**
> *"Finally, look at our real-time performance analytics:*
> - *Our **CPU Utilization** remained at over 85%, proving that safety-blocking a process does not waste CPU cycles because the scheduler context-switches to ready tasks.*
> - *The **Dual-Engine Live Inspector** on the right streams kernel events at millisecond precision, documenting every dispatch, safety check, and aging trigger.*
> - *And the student or examiner can even select **Load From Current Database State** to test their own custom processes and resources created on the dashboard.*
> 
> *This transforms our project from a simple textbook matrix calculator into a complete, authentic Operating Systems simulator."*

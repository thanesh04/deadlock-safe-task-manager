# Academic Viva & Teacher Demonstration Script (10–15 Minutes)

This document is your **word-for-word spoken guide** for presenting the Deadlock-Safe Task Manager to your professor, lab instructor, or external viva examiner.

---

## 1. Quick Presentation Checklist Before You Call the Examiner

- [ ] Make sure the server is running (`python app.py` on `http://127.0.0.1:5000`).
- [ ] Open the web app in full-screen (`F11`).
- [ ] Click **Reset** in the top navigation bar to ensure the default safe textbook state is active.
- [ ] Have this script or mental outline ready.

---

## 2. Opening Pitch (1 Minute)

> **What to Say:**
> *"Good morning, Sir/Madam. For my Operating Systems project, I have built the **Deadlock-Safe Task Manager**.*
> 
> *Traditional operating system task managers, such as Windows Task Manager, only display passive hardware utilization—like CPU and RAM percentages. They do not model how processes compete for discrete resources, nor do they prevent deadlocks using Banker's Algorithm or visualize circular wait dependencies.*
> 
> *Our project is a full-stack educational Operating Systems simulation. It implements Dijkstra's Banker's Algorithm for deadlock avoidance, a multi-instance Deadlock Detection algorithm, dynamic Resource Allocation and Wait-For Graphs using Cytoscape.js, and automated deadlock recovery.*
> 
> *Crucially, all processes and resources inside the simulation are theoretical mathematical models stored in an SQLite database. To demonstrate low-level systems programming, we also created a separate Host OS Monitor using Python's `psutil` library that inspects real Windows hardware without interfering with the simulation.*
> 
> *Let me demonstrate the complete workflow."*

---

## 3. Step-by-Step Demonstration Sequence

---

### STEP 1: The Dashboard Overview (`/`)

- **Action**: Show the main Dashboard.
- **What to Say**:
  > *"Here on the Dashboard, we see our simulated OS environment. At a glance, the system safety card shows that the system is currently in a **SAFE** state with zero deadlocks.*
  > 
  > *We have 5 simulated processes—$P_0$ through $P_4$—and 3 resource types—$R_0, R_1, R_2$. The donut chart visualizes the distribution of process states, while the stacked bar chart compares allocated versus available resources in real time."*

---

### STEP 2: Simulated Processes (`/processes`)

- **Action**: Click **Processes** in the sidebar.
- **What to Say**:
  > *"On the Processes page, we can inspect our simulated processes. I want to emphasize: **$P_0$ through $P_4$ are not Windows processes**. They are software models representing tasks such as a Web Server, Database Worker, or Analytics Engine.*
  > 
  > *Each process maintains its allocated vector, maximum demand, and remaining need. From here, we can create custom processes, request or release resources, or terminate processes."*

---

### STEP 3: Simulated Resources (`/resources`)

- **Action**: Click **Resources** in the sidebar.
- **What to Say**:
  > *"On the Resources page, we manage our multi-instance resource pool. For example, $R_0$ models 10 CPU cores, $R_1$ models 5 GB of RAM, and $R_2$ models 7 disk channels.*
  > 
  > *The system guarantees the fundamental OS invariant: Available equals Total minus the sum of Allocated instances across all processes. The system prevents over-allocation and prohibits deleting any resource that is currently held by a running process."*

---

### STEP 4: Operating System Matrices & Vectors (`/matrices`)

- **Action**: Click **System Matrices** in the sidebar.
- **What to Say**:
  > *"This page displays the exact formal matrices taught in our Operating Systems syllabus:*
  > 1. *The **Available Vector**: We have $[3, 3, 2]$ free units.*
  > 2. *The **Allocation Matrix**: Shows what each process currently holds. For instance, $P_2$ holds 3 units of $R_0$ and 2 units of $R_2$.*
  > 3. *The **Maximum Demand Matrix**: Declares the upper bound of what each process will ever need.*
  > 4. *The **Need Matrix**: Calculated dynamically as $\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$. For example, $P_0$'s need is $[7, 4, 3]$."*

---

### STEP 5: Running Banker's Safety Algorithm (`/safety`)

- **Action**: Click **Safety Analysis** in the sidebar. Click **RUN SAFETY ALGORITHM**.
- **What to Say**:
  > *"Now let us execute Dijkstra's Banker's Algorithm. When I click 'RUN SAFETY ALGORITHM', the backend evaluates the safety condition:*
  > 
  > *It initializes a Work vector equal to Available $[3, 3, 2]$. In Step 1, it discovers that process $P_1$'s remaining need $[1, 2, 2]$ is less than or equal to Work. Therefore, $P_1$ can safely finish and release its allocated resources back into Work.*
  > 
  > *It continues round-robin and finds a complete safe execution sequence:*
  > $$\mathbf{P_1 \to P_3 \to P_0 \to P_2 \to P_4}$$
  > *Because all processes can finish without deadlocking, the system is certified in a **SAFE STATE**."*

---

### STEP 6: Banker's Resource-Request Evaluation (`/resource-request`)

- **Action**: Click **Demo Resource Request** in the topbar dropdown.
- **What to Say**:
  > *"Now, let's see how the OS handles dynamic resource requests.*
  > 
  > *Here, process $P_1$ requests $[R_0=1, R_1=0, R_2=2]$. When I click 'Evaluate & Allocate Request', the algorithm tests the 5-step decision pipeline:*
  > - *Step 1: Is Request $\le$ Need? Yes, $P_1$ needs $[1, 2, 2]$.*
  > - *Step 2: Is Request $\le$ Available? Yes, Available is $[3, 3, 2]$.*
  > - *Step 3: Tentatively simulate allocation in memory.*
  > - *Step 4: Run the Safety Algorithm on the tentative state.*
  > - *Step 5: A safe sequence is found, so the request is **GRANTED** and committed to the database!*
  > 
  > *Conversely, if a process requests resources that would leave the system with insufficient liquidity, the algorithm detects an unsafe state, **DENIES** the request, and rolls back the allocation."*

---

### STEP 7: Deadlock Detection & Graph Visualization (`/deadlock-detection` & `/graphs`)

- **Action**: In the Demo Mode dropdown, click **Demo Deadlock (2 Processes)**.
- **What to Say**:
  > *"Now let us demonstrate an active deadlock. I will load the Two-Process Deadlock scenario.*
  > 
  > *Here, $P_1$ holds Scanner $R_1$ and requests Printer $R_2$. Simultaneously, $P_2$ holds Printer $R_2$ and requests Scanner $R_1$. This is the classic mutual Hold-and-Wait condition.*
  > 
  > *When I click 'RUN DEADLOCK DETECTION', our multi-instance detection algorithm runs. Notice that unlike Banker's Algorithm, this algorithm does not require maximum claims—it directly analyzes active requests.*
  > 
  > *The result is immediate: **DEADLOCK DETECTED! Deadlocked: P1, P2**."*

- **Action**: Click **Graphs (RAG / WFG)** in the sidebar.
- **What to Say**:
  > *"If we navigate to the Graphs screen, Cytoscape.js renders our Resource Allocation Graph. We see process circles and resource rectangles.*
  > 
  > *If I switch to the **Wait-For Graph**, the resource nodes are collapsed to reveal a direct cycle: $P_1 \to P_2 \to P_1$. Our cycle detection algorithm has highlighted the deadlocked loop in bold red."*

---

### STEP 8: Deadlock Recovery

- **Action**: Return to `/deadlock-detection`. In the recovery panel, select victim process $P_1$ and click **Terminate Victim**.
- **What to Say**:
  > *"Because a deadlock cannot resolve itself, the OS must intervene. In the Deadlock Recovery panel, we select process $P_1$ as our termination victim.*
  > 
  > *When I click 'Terminate Victim', the system sets $P_1$'s state to TERMINATED, reclaims all resources it held, and returns them to Available.*
  > 
  > *The system automatically re-runs deadlock detection, and as you can see: **DEADLOCK RESOLVED!** $P_2$ is now unblocked and able to complete."*

---

### STEP 9: Real Host OS Monitor (`/monitor`)

- **Action**: Click **Real OS Monitor** in the sidebar.
- **What to Say**:
  > *"Finally, let us look at the Real Host OS Monitor.*
  > 
  > *This page is fundamentally different from the previous screens. Here, we use Python's `psutil` library to read actual, live telemetry from my Windows laptop at runtime: host CPU utilization, physical RAM in gigabytes, and the 240+ actual Windows background processes.*
  > 
  > *We built a strict architectural firewall between this telemetry and our simulation: real host metrics are **never** fed into Banker's Algorithm, ensuring that the theoretical simulation remains mathematically pure while showcasing our systems programming skills."*

---

## 4. Closing Statement

> *"In conclusion, our Deadlock-Safe Task Manager provides an end-to-end, mathematically accurate, and visually compelling implementation of core Operating Systems principles—covering avoidance, detection, graph modeling, and recovery.*
> 
> *Thank you, Sir/Madam. I am now ready for any viva questions."*

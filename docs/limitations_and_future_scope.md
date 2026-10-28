# Project Limitations & Future Scope

## 1. Technical Limitations of the Current Implementation

While the **Deadlock-Safe Task Manager** provides a rigorous, mathematically accurate, and interactive educational model of operating systems concepts, it operates under several defined technical boundaries:

### 1. Simulated vs. Kernel-Level Processes
- The processes ($P_0$–$P_4$) are application-level database rows in an SQLite database.
- They are not real kernel threads, which means they do not perform true concurrent thread synchronization (e.g., POSIX pthread mutexes, semaphores, or Win32 critical sections).

### 2. Theoretical vs. Hardware Resource Allocations
- The resource types ($R_0$ CPU, $R_1$ Memory, $R_2$ Disk) are discrete integer tokens.
- The simulation does not interface with the Memory Management Unit (MMU) for virtual memory paging or CPU affinity masks.

### 3. Presupposition of Known Maximum Demand
- Like the textbook Banker's Algorithm itself, the avoidance engine requires processes to declare their Maximum Demand in advance.
- In real general-purpose desktop operating systems (Windows, Linux, macOS), modern applications cannot accurately predict their peak lifetime memory or file handle requirements, which is why commercial OSs rarely use Banker's Algorithm directly.

### 4. Read-Only Nature of Host Telemetry (`psutil`)
- The `psutil` monitor screen (`/monitor`) provides read-only observation of real host hardware. It cannot throttle, suspend, or prioritize actual Windows processes based on simulated deadlock status.

### 5. Simulated Preemption Without Checkpointing
- In this implementation, resource preemption is an educational simulation that tests whether transferring a resource unit resolves a circular wait.
- It does not implement low-level application state checkpointing, register saving, or rollback journals required for real process preemption.

---

## 2. Realistic Future Scope & Potential Enhancements

To build upon this academic foundation, future work could extend the project in the following directions:

### 1. Multi-Threaded Process Simulation with Real Synchronization Primitives
- Implement simulated processes as genuine concurrent Python worker threads (`threading.Thread`).
- Model resources as true concurrency locks (`threading.Semaphore`, `threading.Lock`) to demonstrate real thread contention, spinlocks, and sleep-wait behavior.

### 2. Priority-Based Victim Selection Heuristics for Recovery
- Incorporate multi-criteria victim selection algorithms during deadlock recovery:
  - Process Priority (avoid terminating high-priority tasks).
  - CPU Time Expended (favor terminating younger tasks to minimize lost computation).
  - Number of Resources Held (terminate the process that releases the most resources).

### 3. Aging and Starvation Prevention
- Implement an aging mechanism for processes that are repeatedly denied resource requests by Banker's Algorithm, preventing indefinite postponement (starvation).

### 4. Live Kernel Sandboxing via Docker / Linux Cgroups
- Extend the application to manage actual lightweight Linux processes running inside isolated Docker containers.
- Use Linux `cgroups` (control groups) to apply real CPU and RAM resource limits dynamically when Banker's Algorithm commits allocations.

### 5. WebSockets for Real-Time Millisecond State Streaming
- Upgrade client-server communication from HTTP polling to bidirectional WebSockets (`Flask-SocketIO`), enabling real-time animated token passing across the Cytoscape.js graphs as resources are requested, granted, and released.

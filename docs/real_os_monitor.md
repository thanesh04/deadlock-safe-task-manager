# Real Host OS Monitor (psutil): Telemetry & Architectural Isolation

## 1. Overview: The Host Operating System Monitor Page

When you open the **Real OS Monitor** page (`/monitor`) in the application, you see live hardware gauges, progress bars, and metrics for CPU utilization, RAM usage, swap file usage, core counts, and total active Windows processes.

This document answers every question about how this telemetry works and why it is **strictly isolated** from the simulated deadlock algorithms.

---

## 2. Key Questions & Answers for Students and Viva Examiners

### Q1. Is this page actually analyzing my computer?
**YES.** Unlike the simulation screens (which manipulate mathematical matrices stored in SQLite), the `/monitor` page analyzes your actual, physical computer. When you see 18% CPU usage or 9.4 GB RAM used, those are real telemetry measurements taken from your Windows operating system at that exact second.

### Q2. What does `psutil` read?
`psutil` (Python System and Process Utilities) is a cross-platform Python library that queries the Windows kernel (via Windows API / WMI) to extract hardware and process metrics:
```python
@api_bp.route('/system-monitor', methods=['GET'])
def get_real_system_monitor():
    cpu_percent = psutil.cpu_percent(interval=None)
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()
    os_proc_count = len(psutil.pids())
    ...
```

### Q3. Is CPU usage real?
**YES.** `psutil.cpu_percent()` measures the percentage of CPU time spent by your real physical processor across all real applications currently running on your PC.

### Q4. Is RAM usage real?
**YES.** `psutil.virtual_memory()` queries Windows for the exact total physical RAM installed (e.g., 16.0 GB) and the exact number of gigabytes currently occupied by Windows and running background applications.

### Q5. Is OS process count real?
**YES.** `len(psutil.pids())` returns the actual count of Process Control Blocks (PCBs) currently active in your Windows kernel (typically between 150 and 350 on a typical Windows machine).

### Q6. Does this information come from the simulation?
**NO.** None of this information comes from the simulated database models. It is polled directly from your Windows hardware and operating system kernel every 3 seconds.

### Q7. Does this information affect Banker's Algorithm?
**NO. ABSOLUTELY NOT.** The real CPU percentage and physical RAM metrics are **NEVER** fed into Banker's Algorithm, the Safety Algorithm, or Deadlock Detection. 

### Q8. Does Banker's Algorithm affect my actual computer?
**NO.** Running the Banker's Algorithm evaluates the simulated matrices ($Available$, $Allocation$, $Need$). It does not claim your physical RAM or alter your hardware CPU allocation.

### Q9. Why is this feature included in an Operating Systems project?
It serves two pedagogical purposes:
1. **Contrast & Pedagogical Clarity**: It gives students a tangible contrast between *observing raw hardware performance* (what commercial task managers do) versus *modeling resource allocation logic* (what OS kernel schedulers theoretically do).
2. **Comprehensive OS Exploration**: It demonstrates proficiency in low-level Python system programming (`psutil`) alongside theoretical computer science algorithms.

---

## 3. The Academic Firewall: Why Separation is Critical

In a viva examination, examiners frequently test whether students understand the difference between a **simulator** and a **kernel hook**:

```
┌────────────────────────────────────────────────────────┐
│                   REAL HOST COMPUTER                   │
│   Windows 10/11 Kernel ──► Hardware CPU / RAM / Disk   │
│             │                                          │
│             ▼ (READ-ONLY Query via psutil)             │
│   ┌──────────────────────────────┐                     │
│   │ /monitor Screen Only         │                     │
│   └──────────────────────────────┘                     │
└────────────────────────────────────────────────────────┘
                    ║
          ACADEMIC FIREWALL (ZERO DATA COUPLING)
                    ║
┌────────────────────────────────────────────────────────┐
│               SIMULATED OS ENVIRONMENT                 │
│   SQLite Database ──► In-Memory Matrices               │
│   - Processes: P0, P1, P2, P3, P4                      │
│   - Resources: R0 (10), R1 (5), R2 (7)                 │
│             │                                          │
│             ▼                                          │
│   ┌──────────────────────────────────────────────┐     │
│   │ Banker's Safety Algorithm & Request Stepper │     │
│   │ Deadlock Detection Algorithm                 │     │
│   │ Cytoscape.js RAG & Wait-For Graphs           │     │
│   └──────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────┘
```

### Why Real OS Processes CANNOT Be Fed into Banker's Algorithm:
1. **The Maximum Demand Requirement**: Banker's Algorithm strictly requires every process to state its maximum resource claim in advance. Real-world applications (like Google Chrome, Spotify, or Discord) do not know in advance how much memory or CPU they will need over their lifetime.
2. **Mutual Exclusion & Allocation Granularity**: Windows processes share CPU through time-slicing and preemptive thread scheduling, whereas Banker's Algorithm models non-preemptive discrete resource instances.
3. **Safety Guarantee**: Attempting to hook real Windows processes into a theoretical avoidance algorithm would cause deadlocks or crash system drivers.

---

## 4. Summary Table

| Attribute | Real Host Monitor (`/monitor`) | Deadlock Simulation (`/`, `/matrices`, `/safety`) |
| :--- | :--- | :--- |
| **Data Origin** | Windows Kernel APIs via `psutil` | SQLite database `instance/database.db` |
| **CPU Measurement** | Actual hardware CPU clock usage % | Logical integer instances of resource $R_0$ (e.g., 10) |
| **RAM Measurement** | Actual physical DDR RAM gigabytes | Logical integer instances of resource $R_1$ (e.g., 5) |
| **Processes Tracked**| Real Windows tasks (PID 1420, 8932) | Theoretical models ($P_0, P_1, P_2, P_3, P_4$) |
| **Input to Banker's?**| **NO (100% Isolated)** | **YES (Sole input to Banker's)** |
| **Host System Risk** | Zero (Read-only observation) | Zero (In-memory simulation) |

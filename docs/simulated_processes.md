# Simulated Processes in Deadlock-Safe Task Manager

## 1. Overview: What are the "Simulated OS Processes"?

In this application, **Simulated OS Processes** are software data objects representing theoretical execution threads or tasks competing for shared system resources. 

They are defined in the Python code via the `Process` SQLAlchemy model inside `database/models.py`:
```python
class Process(db.Model):
    __tablename__ = 'processes'
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(20), default=ProcessState.READY, nullable=False)
    created_at = db.Column(db.DateTime, default=...)
    completed_at = db.Column(db.DateTime, nullable=True)
```

Each simulated process has:
- A unique logical **PID** string (e.g., `P0`, `P1`, `P2`, `P3`, `P4`).
- A human-readable **Name** (e.g., `Web Server`, `Database Worker`, `Analytics Engine`).
- A lifecycle **State** (`NEW`, `READY`, `RUNNING`, `WAITING`, `BLOCKED`, `COMPLETED`, `DEADLOCKED`, `TERMINATED`).
- An associated **Allocation Vector** (units of resources currently held).
- An associated **Maximum Claim Vector** (maximum units the process will ever require).
- A dynamically calculated **Need Vector** ($\text{Need} = \text{Maximum} - \text{Allocation}$).
- Optional **Pending Requests**.

---

## 2. Comprehensive Q&A on Simulated Processes

### Q1. What are the "Simulated OS Processes"?
They are application-level mathematical models stored as rows in an SQLite database. They act as test subjects for running Dijkstra's Banker's Algorithm, evaluating resource requests, finding safe sequences, and demonstrating circular-wait deadlocks.

### Q2. Are P0, P1, P2, P3, P4 real Windows processes?
**NO.** $P_0, P_1, P_2, P_3, P_4$ are **NOT** real Windows processes. If you press `Ctrl + Shift + Esc` on your keyboard to open Windows Task Manager, you will **not** find any processes named `P0` or `P1`. They do not have Windows PIDs, they do not execute machine instructions on your CPU, and they do not have virtual memory address spaces.

### Q3. Were they automatically taken from my computer?
**NO.** The application never scans your computer's task list to populate the simulation. They are created either by loading predefined textbook scenarios or by user input in the application.

### Q4. How are they created?
Simulated processes are created in two ways:
1. **Via the Web Interface**: Clicking **New Process** on the `/processes` page submits a form with a PID, process name, maximum claims, and initial allocations to `POST /api/processes`.
2. **Via Predefined Scenarios**: Loading a scenario (such as `safe_state` or `two_process_deadlock`) populates predefined process records into the database.

### Q5. Can the user manually create them?
**YES.** You can create as many arbitrary processes as you like by navigating to `/processes` and clicking **New Process**. You can give them any PID (e.g., `P5`, `T100`), declare their maximum demand for each resource, and specify how many instances are initially allocated.

### Q6. Can predefined scenarios create them?
**YES.** Predefined scenarios defined in `simulation/scenarios.py` include predefined lists of processes configured to represent classic textbook scenarios (e.g., Silberschatz 5-process model).

### Q7. What does P0/P1/P2/P3/P4 represent?
They represent concurrent operating system programs that need system resources to finish their work:
- **P0**: Represents a Web Server process handling network I/O.
- **P1**: Represents a Database Worker executing SQL queries.
- **P2**: Represents an Analytics Engine performing heavy computation.
- **P3**: Represents an In-Memory Cache Service.
- **P4**: Represents a Background Backup Agent.

### Q8. What happens when a simulated process requests a resource?
1. The request vector is checked against the process's remaining **Need**.
2. The request vector is checked against system **Available** resources.
3. The Banker's Algorithm simulates allocating those units tentatively.
4. If the resulting state has a safe sequence, the database record is updated (allocation increments, available decrements, process state becomes `RUNNING`).
5. If unsafe, the request is denied and the process state is set to `WAITING`.

### Q9. What happens when a simulated process releases a resource?
1. The process's held allocation counter in the database is decremented.
2. The system's available instances counter is incremented by the same amount.
3. The process's remaining Need increases accordingly ($\text{Need} = \text{Maximum} - \text{Allocation}$).
4. An audit event `RESOURCE_RELEASED` is logged in the `event_logs` table.

### Q10. What happens when a simulated process is terminated?
1. Its state in the database is updated to `TERMINATED`.
2. Every resource instance it was holding is reclaimed and added back to the system's `Available` pool.
3. Its pending requests are marked as `CANCELLED`.
4. The process remains visible in the logs for historical audit purposes.

### Q11. Does terminating P1 terminate a real Windows process?
**NO.** Absolutely not. Terminating $P_1$ executes:
```python
process.state = ProcessState.TERMINATED
for a in process.allocations:
    a.resource.available_instances += a.allocated
    a.allocated = 0
db.session.commit()
```
It simply updates a record in your SQLite database. It does **not** call Windows `TerminateProcess()` or Python `os.kill()`. Your real Windows programs are completely unaffected.

### Q12. Does requesting CPU/memory from this application actually change my computer's CPU/RAM?
**NO.** When $P_1$ requests 2 units of `Memory (GB)` ($R_1$), it only subtracts the integer `2` from the database column `resources.available_instances`. It does **not** make any system calls to Windows kernel memory managers (`VirtualAlloc` or `malloc`). Your physical RAM usage remains completely unchanged.

---

## 3. Process States Reference Table

| State | Color Badge | Meaning in Simulation |
| :--- | :--- | :--- |
| `READY` | Gray / Secondary | Process is created and waiting to be scheduled; has 0 allocated resources. |
| `RUNNING` | Blue | Process holds allocated resources and is actively simulating execution. |
| `WAITING` | Yellow / Warning | Process submitted a resource request that could not be satisfied immediately because units were unavailable. |
| `BLOCKED` | Orange | Process has an outstanding request that cannot be satisfied. |
| `DEADLOCKED` | Red (Pulsing) | Process was evaluated by `DeadlockDetectionAlgorithm` and is caught in an unresolvable circular wait. |
| `COMPLETED` | Green | Process has finished its work and released all resources back to the available pool. |
| `TERMINATED` | Dark Gray | Process was forcibly killed by the user/deadlock recovery to reclaim its resources. |

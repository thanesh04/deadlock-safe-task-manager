# Simulated Resources in Deadlock-Safe Task Manager

## 1. Overview: What are R0, R1, and R2?

In this application, **Simulated Resources** represent consumable or shareable system components that processes compete for.

In the default textbook dataset (`safe_state`):
- **`R0`**: Represents **CPU Cores** (Total: 10 instances).
- **`R1`**: Represents **Memory (GB)** (Total: 5 instances).
- **`R2`**: Represents **Disk Channels** (Total: 7 instances).

In other scenarios, you will see resources representing:
- **`GPU Unit`** (graphics processing acceleration cards)
- **`Database Connection`** (connection pool handles)
- **`Scanner` / `Printer`** (exclusive I/O peripherals)

These are logical labels and integer counters defined in `database/models.py`:
```python
class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.String(20), unique=True, nullable=False) # e.g. 'R0'
    name = db.Column(db.String(100), nullable=False)                   # e.g. 'CPU Core'
    total_instances = db.Column(db.Integer, default=1)                # e.g. 10
    available_instances = db.Column(db.Integer, default=1)            # e.g. 3
```

---

## 2. Comprehensive Q&A on Simulated Resources

### Q1. Are these real CPU cores?
**NO.** $R_0$ does not map to your physical AMD Ryzen or Intel Core processors. It is purely an integer number (10) stored in the SQLite database to model a 10-core machine in an Operating Systems textbook exercise.

### Q2. Is R0 actually reserving CPU cores?
**NO.** When $R_0$ is allocated to process $P_1$, the code does **not** bind any Windows threads to processor affinity masks, nor does it consume CPU clock cycles.

### Q3. Is R1 actually allocating RAM?
**NO.** When $R_1$ ("Memory (GB)") has 5 instances and 2 are allocated to $P_0$, your computer does not allocate 2 gigabytes of physical RAM. It merely executes:
$$\text{available\_instances} = 5 - 2 = 3$$

### Q4. Is R2 actually controlling disk channels?
**NO.** $R_2$ does not control the SATA or NVMe controller on your motherboard. It is a logical token.

### Q5. Are these synchronized with Windows?
**NO.** There is no synchronization between these simulated resources and your Windows device manager or hardware performance counters.

### Q6. What does "10 total, 7 allocated, 3 available" mean?
This expresses the fundamental mathematical resource invariant in operating systems:
- **Total ($Total_j = 10$)**: The maximum capacity of resource $R_j$ present in the simulated system.
- **Allocated ($\sum_i Allocation_{ij} = 7$)**: The sum of units of $R_j$ currently held by all simulated processes combined.
  For example, in the default safe state:
  - $P_0$ holds $0$
  - $P_1$ holds $2$
  - $P_2$ holds $3$
  - $P_3$ holds $2$
  - $P_4$ holds $0$
  - Total allocated = $0 + 2 + 3 + 2 + 0 = 7$.
- **Available ($Available_j = 3$)**: Unallocated units currently free in the system resource pool:
  $$Available_j = Total_j - \sum_{i=0}^{n-1} Allocation_{ij} = 10 - 7 = 3$$

### Q7. Who changes these values?
1. **The User**: By creating resources, editing their total instances, or requesting/releasing them via the web interface.
2. **The Banker's Algorithm**: By tentatively or permanently decrementing $Available$ when granting requests.
3. **The Recovery Engine**: By returning all held resources back to $Available$ when a victim process is terminated.

### Q8. What happens when a simulated process requests R0?
If process $P_1$ requests 1 unit of $R_0$:
1. The Banker's Algorithm verifies that $1 \le Need[P_1][R_0]$ and $1 \le Available[R_0]$.
2. If safe, $Available[R_0]$ drops from 3 to 2, and $Allocation[P_1][R_0]$ increases from 2 to 3.
3. The remaining $Need[P_1][R_0]$ drops from 1 to 0.

### Q9. Does this affect the actual machine?
**NO.** Your physical computer experiences zero hardware change. Only records in the SQLite database file (`instance/database.db`) and frontend HTML tables are updated.

---

## 3. Resource Invariants Enforced by the System

The application strictly enforces these mathematical rules in `simulation/validation.py` and `simulation/resource_manager.py`:
1. **Non-negativity**:
   $$Available_j \ge 0 \quad \text{for all } j$$
2. **Capacity Limit**:
   $$\sum_{i=0}^{n-1} Allocation_{ij} \le Total_j$$
3. **Safe Modification**:
   A user is **prohibited** from reducing $Total_j$ below the currently allocated amount ($\sum_i Allocation_{ij}$).
4. **Safe Deletion**:
   A user is **prohibited** from deleting a resource if any simulated process is currently holding at least one allocated unit of that resource.

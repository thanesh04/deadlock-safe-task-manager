# Operating System Matrices & Vectors Guide

When you navigate to **System Matrices** (`/matrices`) in the Deadlock-Safe Task Manager, you are viewing the formal mathematical state of the operating system.

In textbooks (such as Silberschatz & Galvin), resource allocation state is formally defined by $n$ processes and $m$ resource types using **1 vector** and **3 matrices**.

---

## 1. Overview of the Structure

- **Rows**: Represent simulated **Processes** ($P_0, P_1, P_2, P_3, P_4$).
- **Columns**: Represent simulated **Resource Types** ($R_0, R_1, R_2$).

For example, when the table displays:
$$\begin{matrix} & R_0 & R_1 & R_2 \\ P_2 & 3 & 0 & 2 \end{matrix}$$

This means: **Process $P_2$ currently holds 3 units of $R_0$ (CPU Cores), 0 units of $R_1$ (Memory), and 2 units of $R_2$ (Disk Channels).**

---

## 2. The Four Data Structures Explained

### 1. Available Vector ($\text{Available}[m]$)

#### What it represents:
A 1D vector of length $m$ indicating the number of free, unassigned instances of each resource type currently available in the system pool.

#### Why it is required:
The operating system must know how many units are free before it can decide whether a process's request can be satisfied immediately.

#### How it is calculated:
$$\text{Available}[j] = \text{Total}[j] - \sum_{i=0}^{n-1} \text{Allocation}[i][j]$$

#### How Banker's Algorithm uses it:
At the start of the Safety Algorithm, the temporary work vector is initialized to Available:
$$\text{Work} = \text{Available}$$

#### Current numerical example (from `safe_state`):
$$\text{Available} = \begin{bmatrix} R_0 & R_1 & R_2 \\ 3 & 3 & 2 \end{bmatrix}$$
- 3 free units of CPU ($R_0$)
- 3 free units of Memory ($R_1$)
- 2 free units of Disk ($R_2$)

---

### 2. Allocation Matrix ($\text{Allocation}[n \times m]$)

#### What it represents:
A 2D matrix of size $n \times m$ defining the number of resources of each type currently allocated to each process.

#### Why it is required:
The OS tracks which resources each process is holding (the *Hold* in *Hold and Wait*). When a process completes, the OS reclaims these allocated units.

#### How Banker's Algorithm uses it:
When process $P_i$ can satisfy its need ($\text{Need}[i] \le \text{Work}$), the algorithm assumes $P_i$ will finish and release all its held resources back to the pool:
$$\text{Work} = \text{Work} + \text{Allocation}[i]$$

#### Current numerical example (from `safe_state`):
$$\text{Allocation} = \begin{matrix}
& R_0 & R_1 & R_2 \\
P_0 & 0 & 1 & 0 \\
P_1 & 2 & 0 & 0 \\
P_2 & 3 & 0 & 2 \\
P_3 & 2 & 1 & 1 \\
P_4 & 0 & 0 & 2
\end{matrix}$$

---

### 3. Maximum Demand Matrix ($\text{Maximum}[n \times m]$)

#### What it represents:
A 2D matrix defining the maximum number of instances of each resource that each process may request during its execution.

#### Why it is required:
Deadlock **Avoidance** (unlike Deadlock Detection) requires *a priori* knowledge: the OS must know the worst-case future demand of every process so it never enters an unsafe state from which deadlock is inevitable.

#### How Banker's Algorithm uses it:
It defines the upper bound. A process can never request more than its declared Maximum.

#### Current numerical example (from `safe_state`):
$$\text{Maximum} = \begin{matrix}
& R_0 & R_1 & R_2 \\
P_0 & 7 & 5 & 3 \\
P_1 & 3 & 2 & 2 \\
P_2 & 9 & 0 & 2 \\
P_3 & 2 & 2 & 2 \\
P_4 & 4 & 3 & 3
\end{matrix}$$

---

### 4. Remaining Need Matrix ($\text{Need}[n \times m]$)

#### What it represents:
A 2D matrix indicating the remaining resources each process may still request to complete its execution.

#### Why it is required:
The OS must check whether available resources can satisfy what a process **might still ask for** before it guarantees that the process will not get stuck.

#### How it is calculated:
$$\text{Need}[i][j] = \text{Maximum}[i][j] - \text{Allocation}[i][j]$$

#### How Banker's Algorithm uses it:
The core check of the safety algorithm tests:
$$\text{Need}[i][j] \le \text{Work}[j] \quad (\forall j)$$
If this condition holds, process $P_i$ is guaranteed to be able to complete.

#### Current numerical calculation (from `safe_state`):
For $P_0$:
- $R_0: 7 - 0 = 7$
- $R_1: 5 - 1 = 4$
- $R_2: 3 - 0 = 3$
- Therefore, $\text{Need}[P_0] = [7, 4, 3]$

For all processes:
$$\text{Need} = \begin{matrix}
& R_0 & R_1 & R_2 \\
P_0 & 7 & 4 & 3 \\
P_1 & 1 & 2 & 2 \\
P_2 & 6 & 0 & 0 \\
P_3 & 0 & 1 & 1 \\
P_4 & 4 & 3 & 1
\end{matrix}$$

---

## 3. Matrix Consistency Rules Enforced by the Code

In `simulation/validation.py`, the method `validate_matrix_consistency()` verifies:
1. $\text{Need}[i][j] \ge 0$: A process can never be allocated more than its maximum demand.
2. $\text{Allocation}[i][j] \ge 0$ and $\text{Maximum}[i][j] \ge 0$: Negative quantities are strictly rejected.
3. $\sum_{i} \text{Allocation}[i][j] + \text{Available}[j] = \text{Total}[j]$: Resources cannot be created or destroyed; every single instance is accounted for as either allocated or available.

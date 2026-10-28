# Banker's Algorithm (Deadlock Avoidance) Guide

## 1. What is Banker's Algorithm?

The **Banker's Algorithm** is a classic resource allocation and **deadlock avoidance** algorithm developed by Dutch computer scientist **Edsger Dijkstra**. 

The analogy comes from banking: a small-town bank has a limited amount of cash to distribute among several clients who have pre-agreed lines of credit (maximum limits). The banker will never allocate cash to a client if the remaining cash in the vault is insufficient to satisfy at least one client's remaining credit line to completion. By ensuring that at least one client can finish their business, repay their entire loan, and return cash to the vault, the bank avoids running out of liquidity (deadlock).

---

## 2. Why is it Called an "Avoidance" Algorithm?

It is vital not to confuse **Deadlock Avoidance** with **Deadlock Detection**:
- **Deadlock Avoidance (Banker's Algorithm)**: Operates *proactively*. Before any allocation is granted, the algorithm tests the tentative future state. If granting the request could place the system in an unsafe state where a deadlock might occur later, the request is **avoided (denied or delayed)**.
- **Deadlock Detection**: Operates *reactively*. It allows processes to request resources freely without declaring maximum demands, and periodically scans existing allocations and pending requests to identify whether any processes are currently deadlocked.

> **CRITICAL VIVA DISTINCTION**: Banker's Algorithm does NOT detect an existing deadlock. It prevents deadlocks from occurring by ensuring the system always remains in a **Safe State**.

---

## 3. Safe State, Unsafe State, and Safe Sequence

### Safe State
A state is **safe** if the system can allocate resources to each process (up to its declared maximum) in some order without leading to a deadlock. Formally, a safe state guarantees the existence of a **Safe Sequence**.

### Unsafe State
An **unsafe state** is **NOT** necessarily a deadlock! Rather, an unsafe state is a state from which the operating system cannot guarantee that all processes can finish without deadlocking. An unsafe state has the *potential* to lead to a deadlock if processes request their maximum claims simultaneously.

$$\text{Safe States} \subset \text{All States}$$
$$\text{Deadlock States} \subset \text{Unsafe States}$$

### Safe Sequence
A sequence of processes $\langle P_1, P_3, P_0, P_2, P_4 \rangle$ is a **safe sequence** if, for each $P_i$, the resources that $P_i$ still needs can be satisfied by the currently available resources plus the resources already held by all preceding processes in the sequence.

---

## 4. Key Vectors in the Algorithm: Work and Finish

1. **$\text{Work}[m]$**: A temporary working copy of the Available resource vector. It tracks how many resources will be free as processes hypothetically finish and release their allocations:
   $$\text{Initial: } \text{Work} = \text{Available}$$
2. **$\text{Finish}[n]$**: A boolean array indicating whether process $P_i$ can finish its execution:
   $$\text{Initial: } \text{Finish}[i] = \text{false} \quad (\forall i)$$

---

## 5. Complete Mathematical Algorithm

### Step 1: Initialize
$$\text{Work} = \text{Available}$$
$$\text{Finish}[i] = \text{false} \quad \text{for } i = 0, 1, \dots, n-1$$
$$\text{SafeSequence} = [\,]$$

### Step 2: Search for a Candidate Process
Find an index $i$ such that:
1. $\text{Finish}[i] == \text{false}$
2. $\text{Need}[i][j] \le \text{Work}[j] \quad (\forall j \in \{0, 1, \dots, m-1\})$

If no such $i$ exists, go to **Step 4**.

### Step 3: Simulate Process Completion
If candidate $P_i$ is found:
1. $\text{Work} = \text{Work} + \text{Allocation}[i]$ (reclaim all held resources).
2. $\text{Finish}[i] = \text{true}$.
3. Append $P_i$ to $\text{SafeSequence}$.
4. Return to **Step 2** to find the next candidate.

### Step 4: Evaluate Overall Safety
If $\text{Finish}[i] == \text{true}$ for all $i \in \{0, 1, \dots, n-1\}$, then:
$$\text{System is in a SAFE STATE with safe sequence } \text{SafeSequence}$$
Otherwise:
$$\text{System is in an UNSAFE STATE}$$

---

## 6. Complete Numerical Walkthrough (Default Scenario)

Let:
- Resources: $R_0 = 10, R_1 = 5, R_2 = 7$
- Available: $\text{Work} = [3, 3, 2]$
- Allocation & Maximum matrices as defined in the default `safe_state`.

### Initial State:
$$\text{Work} = [3, 3, 2]$$
$$\text{Finish} = [F, F, F, F, F]$$

### Iteration 1:
- Check $P_0$: $\text{Need}[P_0] = [7, 4, 3]$. Is $[7, 4, 3] \le [3, 3, 2]$? **NO** ($7 > 3$). $P_0$ cannot finish yet.
- Check $P_1$: $\text{Need}[P_1] = [1, 2, 2]$. Is $[1, 2, 2] \le [3, 3, 2]$? **YES!**
  - $\text{Work} = [3, 3, 2] + \text{Allocation}[P_1]([2, 0, 0]) = [5, 3, 2]$.
  - $\text{Finish}[P_1] = \text{true}$.
  - Sequence: $\langle P_1 \rangle$.

### Iteration 2:
With $\text{Work} = [5, 3, 2]$:
- Check $P_3$: $\text{Need}[P_3] = [0, 1, 1]$. Is $[0, 1, 1] \le [5, 3, 2]$? **YES!**
  - $\text{Work} = [5, 3, 2] + \text{Allocation}[P_3]([2, 1, 1]) = [7, 4, 3]$.
  - $\text{Finish}[P_3] = \text{true}$.
  - Sequence: $\langle P_1, P_3 \rangle$.

### Iteration 3:
With $\text{Work} = [7, 4, 3]$:
- Check $P_0$: $\text{Need}[P_0] = [7, 4, 3]$. Is $[7, 4, 3] \le [7, 4, 3]$? **YES!**
  - $\text{Work} = [7, 4, 3] + \text{Allocation}[P_0]([0, 1, 0]) = [7, 5, 3]$.
  - $\text{Finish}[P_0] = \text{true}$.
  - Sequence: $\langle P_1, P_3, P_0 \rangle$.

### Iteration 4:
With $\text{Work} = [7, 5, 3]$:
- Check $P_2$: $\text{Need}[P_2] = [6, 0, 0]$. Is $[6, 0, 0] \le [7, 5, 3]$? **YES!**
  - $\text{Work} = [7, 5, 3] + \text{Allocation}[P_2]([3, 0, 2]) = [10, 5, 5]$.
  - $\text{Finish}[P_2] = \text{true}$.
  - Sequence: $\langle P_1, P_3, P_0, P_2 \rangle$.

### Iteration 5:
With $\text{Work} = [10, 5, 5]$:
- Check $P_4$: $\text{Need}[P_4] = [4, 3, 1]$. Is $[4, 3, 1] \le [10, 5, 5]$? **YES!**
  - $\text{Work} = [10, 5, 5] + \text{Allocation}[P_4]([0, 0, 2]) = [10, 5, 7]$.
  - $\text{Finish}[P_4] = \text{true}$.
  - Sequence: $\langle P_1, P_3, P_0, P_2, P_4 \rangle$.

### Conclusion:
All processes have $\text{Finish}[i] == \text{true}$. The system is in a **SAFE STATE** with safe sequence:
$$\mathbf{P_1 \to P_3 \to P_0 \to P_2 \to P_4}$$

---

## 7. How the Application Implements and Visualizes This

- **Backend Module**: `algorithms/safety.py` implements the class `SafetyAlgorithm`.
- **Trace Dictionary**: For each step, it records:
  ```json
  {
    "step": 1,
    "process": "P1",
    "work_before": {"R0": 3, "R1": 3, "R2": 2},
    "need": {"R0": 1, "R1": 2, "R2": 2},
    "can_finish": true,
    "allocation": {"R0": 2, "R1": 0, "R2": 0},
    "work_after": {"R0": 5, "R1": 3, "R2": 2},
    "decision": "CAN_FINISH"
  }
  ```
- **UI Screen (`/safety`)**: Renders a green success banner with the safe sequence, followed by an interactive timeline stepper detailing every single evaluated step.

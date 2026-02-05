# CPU Scheduling Algorithm Simulator

A comprehensive GUI-based simulator for visualizing and comparing different CPU scheduling algorithms. This tool helps students and professionals understand how various scheduling algorithms work through interactive Gantt charts and performance metrics.

## Table of Contents

- Features
- Setup Instructions
- Algorithms Implemented
- How to Use
- Understanding the Results

## Features

- **5 Scheduling Algorithms**: FCFS, SJF, SRT, Round Robin, and MLFQ
- **Interactive GUI**: Add, edit, and remove processes through dialogs
- **Visual Gantt Charts**: Color-coded timeline visualization
- **Performance Metrics**: Waiting time, turnaround time, and response time
- **Customizable Parameters**: Adjust quantum time for RR and MLFQ
- **Real-time Simulation**: See how each algorithm schedules processes

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the repository**

   ```bash
   git clone -b CPU_Scheduling_Process https://github.com/Nget-Darapich/Operating-System.git
   cd cpu-scheduler
   ```

2. **Install required dependencies**

   ```bash
   pip install tkinter matplotlib
   ```

    Note: `tkinter` usually comes pre-installed with Python. If not:

   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **macOS**: Included with Python installation
   - **Windows**: Included with Python installation

3. **Verify installation**

   ```bash
   python --version  # Should be 3.7+
   python -c "import tkinter; import matplotlib"  # Should run without errors
   ```

### Running the Application

```bash
python cpu_scheduler.py
```

The GUI window will open with sample processes already loaded.

## Algorithms Implemented

### 1. First-Come, First-Served (FCFS)

**Description**: The simplest scheduling algorithm that executes processes in the order they arrive.

**Characteristics**:

- Non-preemptive
- Processes are executed in arrival order
- Can cause convoy effect (short processes wait for long ones)

**Best for**: Batch systems where fairness in order is important

**How it works**:

1. Sort processes by arrival time
2. Execute each process to completion in order
3. No interruption once a process starts

---

### 2. Shortest Job First (SJF)

**Description**: Selects the process with the shortest burst time from all available processes.

**Characteristics**:

- Non-preemptive
- Minimizes average waiting time
- Requires knowledge of burst times in advance
- Can cause starvation of longer processes

**Best for**: Systems where process duration is known and minimizing average wait time is critical

**How it works**:

1. At each decision point, select the process with shortest burst time
2. Execute it to completion
3. Repeat until all processes complete

---

### 3. Shortest Remaining Time (SRT)

**Description**: Preemptive version of SJF that can interrupt a running process if a new process arrives with shorter remaining time.

**Characteristics**:

- Preemptive
- Optimal for minimizing average waiting time
- High context-switching overhead
- Can cause starvation

**Best for**: Interactive systems requiring quick response for short tasks

**How it works**:

1. At each time unit, check for new arrivals
2. Select process with shortest remaining burst time
3. Execute for one time unit
4. Repeat, allowing preemption

---

### 4. Round Robin (RR)

**Description**: Each process gets a fixed time slice (quantum) in a circular queue fashion.

**Characteristics**:

- Preemptive
- Fair allocation of CPU time
- Performance depends on quantum size
- Good response time for interactive systems

**Best for**: Time-sharing systems, interactive applications

**Parameters**:

- **Time Quantum**: CPU time allocated per turn (default: 2)

**How it works**:

1. Maintain a queue of ready processes
2. Give each process one quantum of CPU time
3. If process completes, remove from queue
4. If not complete, move to back of queue
5. Repeat until all processes finish

**Quantum Selection Tips**:

- Too small: High context-switching overhead
- Too large: Degenerates to FCFS
- Recommended: 10-100ms in real systems

---

### 5. Multi-Level Feedback Queue (MLFQ)

**Description**: Uses multiple queues with different priorities and quantum sizes, allowing processes to move between queues based on behavior.

**Characteristics**:

- Preemptive
- Adapts to process behavior
- Prevents starvation while prioritizing interactive processes
- Most complex algorithm

**Best for**: General-purpose operating systems, mixed workload environments

**Parameters**:

- **Base Quantum**: Time slice for highest priority queue
- Queue 0: quantum = base
- Queue 1: quantum = base × 2
- Queue 2: FCFS (infinite quantum)

**How it works**:

1. New processes enter highest priority queue (Queue 0)
2. Process runs for its quantum
3. If it completes, it's removed
4. If quantum expires, it moves to next lower queue
5. Higher priority queues are checked first
6. Processes in Queue 2 run FCFS until completion

**Queue Behavior**:

- **Queue 0** (High Priority): Short quantum, for I/O-bound/interactive tasks
- **Queue 1** (Medium Priority): Longer quantum, for processes needing more CPU
- **Queue 2** (Low Priority): FCFS, for CPU-intensive background tasks

---

## How to Use

### Adding Processes

1. **Click "➕ Add" button**
2. Enter process details in the dialog:
   - **Process ID**: Unique identifier (e.g., P1, P2, Task1)
   - **Arrival Time**: When the process enters the ready queue (0-100)
   - **Burst Time**: CPU time required (1-100)
   - **Priority**: Process priority level (1-10, used for future extensions)
3. Click **OK** to add the process

### Editing Processes

- **Method 1**: Select a process and click "✏️ Edit"
- **Method 2**: Double-click on any process in the table
- Modify values and click **OK**

### Removing Processes

- **Remove one**: Select process and click "🗑️ Remove"
- **Remove all**: Click "🗑️ Clear All" (confirmation required)

### Running Simulations

#### FCFS Simulation

1. Select **FCFS** radio button
2. Click **▶ Run Simulation**
3. View Gantt chart and metrics

#### SJF Simulation

1. Select **SJF** radio button
2. Click **▶ Run Simulation**
3. Compare with FCFS results

#### SRT Simulation

1. Select **SRT** radio button
2. Click **▶ Run Simulation**
3. Observe preemptive behavior in Gantt chart

#### Round Robin Simulation

1. Select **Round Robin** radio button
2. Set **Quantum** value (1-20)
   - Start with 2-4 for typical scenarios
   - Try different values to see impact
3. Click **▶ Run Simulation**
4. Notice time-slice switching in Gantt chart

#### MLFQ Simulation

1. Select **MLFQ** radio button
2. Set **Quantum** for Queue 0 (1-20)
   - Queue 1 automatically gets 2× this value
   - Queue 2 uses FCFS
3. Click **▶ Run Simulation**
4. Observe processes moving between priority levels

## Understanding the Results

### Gantt Chart Tab

- **Visual Timeline**: Shows when each process executes
- **Color Coding**: Each process has a unique color
- **Time Axis**: Shows the progression of time
- **Process Labels**: Process IDs shown in each segment

### Metrics Tab

**Key Performance Indicators**:

| Metric | Description | Formula |
|--------|-------------|---------|

| **Waiting Time** | Time spent in ready queue | Turnaround Time - Burst Time |
| **Turnaround Time** | Total time from arrival to completion | Completion Time - Arrival Time |
| **Response Time** | Time from arrival to first execution | First Start Time - Arrival Time |

**Average Row**: Shows mean values across all processes

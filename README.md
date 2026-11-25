# SystemPulse — Integrated OS Performance Analyzer
### Operating Systems Capstone Project | B.Tech CSE Data Science

---

## 1. Project Overview

**SystemPulse — Integrated OS Performance Analyzer** is an Operating Systems capstone project developed with **Python**, **Streamlit**, **psutil**, **Plotly**, and **Pandas**.

It collects **actual system information** directly from the user's host operating system, displays it in an interactive dark dashboard, persists historical data in CSV files, and evaluates resource usage against configurable safety thresholds to deliver data-driven recommendations.

The application is specifically engineered for a **medium-level B.Tech CSE capstone project**: it avoids overcomplication, focuses on implementing four meaningful modules thoroughly, and connects real-time telemetry to fundamental Operating System concepts.

---

## 2. Core Capstone Modules

SystemPulse implements the four core required modules:

### Module 1: System Dashboard
- **Real OS Telemetry**: Gathers live metrics directly using OS system calls (`psutil`).
- **CPU Utilization**: Real-time processor load percentage, per-core load, and clock frequency.
- **RAM Usage & Available RAM**: Total RAM (GB), Used RAM (GB), and Available RAM (GB) with progress indicator.
- **Disk Usage**: Total storage capacity (GB), Used storage (GB), and Free space (GB).
- **Total Running Processes**: Current count of active processes in the OS task table.
- **Host Metadata**: Hostname, OS distribution, architecture, processor model, and formatted uptime.
- **Visual Allocation Donut Charts**: Interactive breakdown of physical memory and storage pools.

### Module 2: Process Monitor
- **Process Table**: Live table showing Process Name, PID, CPU utilization (%), Memory usage (MB), Memory percentage (%), and State.
- **Searchable**: Search filter by process name or PID.
- **Sortable**: Sort by CPU %, Memory MB, PID, or Process Name in ascending or descending order.
- **Top Resource Consumers**: Horizontal bar charts displaying Top 5 CPU and Top 5 Memory consuming processes.
- **Safe Read-Only Operation**: Safely handles permission boundaries (`AccessDenied`) and terminated processes (`NoSuchProcess`) without crashing or terminating any system process.

### Module 3: Performance Visualization
- **Interactive Time-Series Charts**: Built with Plotly:
  - CPU Utilization over time with configurable threshold line.
  - RAM Utilization over time with configurable threshold line.
  - Synchronized multi-resource comparative overlay (CPU vs RAM vs Disk).
- **Periodic CSV Logging**: Automatically logs timestamped metrics into `data/system_history.csv`.
- **CSV Data Export**: One-click download button for offline evaluation.
- **Log Management**: Ability to reset and clear historical data.

### Module 4: Alerts & System Analysis
- **Configurable Thresholds**: Users can adjust CPU, RAM, and Disk alert thresholds via sidebar sliders.
- **Active Warning Banners**: Visual alert cards when live utilization exceeds thresholds.
- **Measurement-Based Recommendations**:
  - If CPU usage is elevated, identifies the specific culprit process consuming the most CPU cycles.
  - If RAM usage is high, identifies the leading memory-consuming process and warns against disk swapping.
  - If disk space is low, warns against storage exhaustion and virtual memory pagefile failure.
  - If metrics are nominal, displays a healthy system status.

---

## 3. Operating System Concepts Demonstrated

| Operating System Concept | Theoretical Foundation | Practical Implementation in SystemPulse |
| :--- | :--- | :--- |
| **Process Control Block (PCB)** | The kernel data structure storing PID, program counter, CPU registers, and memory pointers. | Process Monitor scans active PCB entries to display PIDs, execution states (running, sleeping), and RSS memory. |
| **Multiprogramming & Scheduling** | The OS allocates quantum slices across processes to maximize CPU utilization. | System Dashboard monitors aggregate and per-core CPU utilization; Process Monitor identifies processes consuming quantum slices. |
| **Memory Management (RAM vs Virtual)** | The OS separates physical memory from virtual address spaces and page caches. | Memory Monitor distinguishes "Used RAM" from "Available RAM" (reclaimable cache buffer), identifying when allocations approach physical limits. |
| **Secondary Storage Allocation** | File system block allocation, directory hierarchy, and partition management. | Disk Monitor tracks partition capacities, used blocks, and remaining unallocated clusters. |
| **Threshold Alerts & Exceptions** | Traps and signals (e.g. `SIGXCPU`, `SIGSEGV`) raised when limits are breached. | Alert Module evaluates tripwires and suggests remedies (such as renicing or closing heavy tasks) to maintain OS equilibrium. |

---

## 4. Project Structure

```
SystemPulse/
│
├── .streamlit/
│   └── config.toml          # Dark theme palette & headless configuration
│
├── app.py                   # Main Streamlit application with the 4 modules
├── run.py                   # One-click launcher script (python run.py)
├── requirements.txt         # Core dependencies: streamlit, psutil, plotly, pandas
├── README.md                # Comprehensive documentation & viva guide
│
├── data/                    # Persistent storage directory
│   ├── system_history.csv   # Real-time telemetry log
│   └── settings.json        # Configured thresholds (CPU, RAM, Disk)
│
├── modules/                 # Modular, understandable backend logic
│   ├── __init__.py
│   ├── monitor.py           # psutil wrappers: CPU, RAM, Disk, System Info
│   ├── process.py           # Process scanner, search, sort, and top consumers
│   ├── history.py           # CSV metric logger and Pandas DataFrame loader
│   └── alerts.py            # Threshold validation, warnings & recommendations
│
├── tests/                   # Automated unit test suite
│   └── test_systempulse.py  # 9 comprehensive tests for all 4 modules
│
└── assets/
    └── style.css            # Clean dark dashboard CSS
```

---

## 5. Technology Stack

- **Python 3.9+**: Core application logic.
- **Streamlit**: Web dashboard framework with interactive widgets and auto-refresh.
- **psutil**: Cross-platform system and process telemetry library.
- **Plotly**: Interactive time-series and comparison charts.
- **Pandas**: Tabular data manipulation, time parsing, and CSV processing.
- **CSV**: Lightweight historical metric storage.

---

## 6. Installation & How to Run

### Step 1: Open Terminal / PowerShell in Project Directory
```powershell
cd C:\Users\tomar\.gemini\antigravity\scratch\SystemPulse
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Application
You can run the application with either command:

**Option A (Recommended Launcher):**
```powershell
python run.py
```

**Option B (Streamlit CLI):**
```powershell
streamlit run app.py
```

Open your browser and navigate to:
👉 **`http://localhost:8501`**

---

## 7. Automated Testing

To run the automated test suite verifying all 4 modules:

```powershell
python tests/test_systempulse.py
```

### Test Suite Output:
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.185s

OK
```

The tests verify:
1. `test_01_system_info`: Host metadata and uptime formatting.
2. `test_02_cpu_metrics`: Total CPU %, per-core load list, frequency.
3. `test_03_memory_and_disk_metrics`: RAM total/used/available, disk total/free.
4. `test_04_process_enumeration`: Safe extraction of PID, name, CPU %, memory MB.
5. `test_05_process_search_and_sort`: Process search filter and multi-column sorting.
6. `test_06_history_logging_and_export`: CSV appending, Pandas loading, headers.
7. `test_07_threshold_save_and_load`: JSON settings persistence and bounds checking.
8. `test_08_alert_triggering`: Threshold violation detection.
9. `test_09_recommendations_culprit_detection`: Identification of culprit processes in high-load states.

---

## 8. Live Demo

- **Preview**: https://system-pulse---integrated-os-performance-analyzer-boza6ftsxlle.streamlit.app/

## 9. Viva & Presentation Questions Guide (For Capstone Defense)

**Q1: How does SystemPulse obtain real CPU metrics without using simulated data?**
> **Answer**: SystemPulse uses the `psutil` library, which interacts directly with OS kernel APIs. On Windows, it queries the Windows Performance Counters and NtQuerySystemInformation API; on Linux, it reads `/proc/stat`.

**Q2: What is the difference between "Used RAM" and "Available RAM"?**
> **Answer**: "Used RAM" is the physical memory allocated to active process working sets. "Available RAM" is the amount of memory that can be immediately allocated to new processes without requiring swapping to disk (it includes free memory plus reclaimable page cache and buffers).

**Q3: How does the application handle permission errors when scanning processes?**
> **Answer**: System processes and processes owned by other users or the kernel are protected by OS privilege rings. When `psutil` attempts to read these processes, it raises `psutil.AccessDenied`. SystemPulse wraps process enumeration inside `try...except (psutil.NoSuchProcess, psutil.AccessDenied)` blocks to ensure smooth operation without crashes.

**Q4: How does SystemPulse identify the root cause of high resource usage?**
> **Answer**: In Module 4 (`alerts.py`), when CPU or RAM utilization crosses the configured threshold, SystemPulse filters and sorts the active process list to identify the specific process consuming the highest percentage of that resource, surfacing its PID and executable name in the recommendation card.

**Q5: Why is time-series logging to CSV useful in Operating Systems monitoring?**
> **Answer**: Instantaneous snapshots do not reveal trends. Recording periodic samples into CSV enables historical capacity planning, identification of memory leaks (steady upward drift in RAM consumption), and analysis of transient CPU spikes.

---


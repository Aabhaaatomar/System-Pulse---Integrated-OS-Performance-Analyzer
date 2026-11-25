"""
SystemPulse - Process Monitor Module
Enumerates active OS processes safely and provides sorting, searching,
and top CPU/memory consumer rankings without terminating processes.
"""

import psutil
from typing import List, Dict, Any


def get_all_processes() -> List[Dict[str, Any]]:
    """
    Safely iterate all active system processes.
    Extracts PID, process name, CPU %, memory usage (MB), and memory %.
    Catches permission errors and terminated processes gracefully.
    """
    processes = []

    # First pass: trigger cpu_percent interval measurement
    procs = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc.cpu_percent(interval=None)
            procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Second pass: read attributes safely
    for proc in procs:
        try:
            with proc.oneshot():
                pid = proc.pid
                name = proc.name() or "Unknown"
                cpu_p = round(max(0.0, proc.cpu_percent(interval=None)), 1)
                
                # Resident Set Size (physical RAM) in MB
                mem_info = proc.memory_info()
                rss_mb = round((mem_info.rss / (1024 * 1024)), 1) if mem_info else 0.0
                mem_p = round(proc.memory_percent(), 1)
                status = proc.status()

                processes.append({
                    "pid": pid,
                    "name": name,
                    "cpu_percent": cpu_p,
                    "memory_mb": rss_mb,
                    "memory_percent": mem_p,
                    "status": status
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return processes


def get_top_processes(processes: List[Dict[str, Any]], n: int = 5, by: str = "cpu") -> List[Dict[str, Any]]:
    """Retrieve top N processes ranked by CPU % or Memory (MB)."""
    if by == "cpu":
        # Exclude System Idle Process (PID 0) from active user ranking
        filtered = [
            p for p in processes
            if p["name"].lower() not in ["system idle process", "idle"] and p["pid"] != 0
        ]
        return sorted(filtered, key=lambda x: x["cpu_percent"], reverse=True)[:n]
    else:
        return sorted(processes, key=lambda x: x["memory_mb"], reverse=True)[:n]


def search_and_sort_processes(
    processes: List[Dict[str, Any]],
    query: str = "",
    sort_by: str = "cpu_percent",
    ascending: bool = False
) -> List[Dict[str, Any]]:
    """Filter processes by search query and sort by the designated column."""
    filtered = processes

    if query:
        q = query.strip().lower()
        filtered = [
            p for p in filtered
            if q in p["name"].lower() or q in str(p["pid"])
        ]

    valid_keys = ["cpu_percent", "memory_mb", "memory_percent", "pid", "name"]
    key = sort_by if sort_by in valid_keys else "cpu_percent"

    return sorted(filtered, key=lambda x: x[key], reverse=not ascending)

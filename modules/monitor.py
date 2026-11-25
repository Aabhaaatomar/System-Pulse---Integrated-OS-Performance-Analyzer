"""
SystemPulse - System Monitor Module
Fetches live hardware, processor, memory, storage, and OS metadata using psutil.
"""

import time
import platform
import psutil
from typing import Dict, Any


def format_uptime(seconds: float) -> str:
    """Format seconds into readable uptime (e.g., '1d 4h 23m 12s')."""
    if seconds <= 0:
        return "0s"
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def get_system_info() -> Dict[str, Any]:
    """Retrieve static OS and hardware profile."""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    return {
        "hostname": platform.node(),
        "os_name": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "Multi-Core Processor",
        "uptime_formatted": format_uptime(uptime_seconds),
        "physical_cores": psutil.cpu_count(logical=False) or 1,
        "logical_cores": psutil.cpu_count(logical=True) or 1
    }


def get_cpu_metrics() -> Dict[str, Any]:
    """Retrieve real-time CPU utilization metrics."""
    total_percent = psutil.cpu_percent(interval=None)
    per_core = psutil.cpu_percent(interval=None, percpu=True)
    
    freq_current = 0.0
    try:
        freq = psutil.cpu_freq()
        if freq:
            freq_current = round(freq.current, 1)
    except Exception:
        pass

    return {
        "total_percent": total_percent,
        "per_core": per_core,
        "freq_mhz": freq_current
    }


def get_memory_metrics() -> Dict[str, Any]:
    """Retrieve physical RAM usage metrics in Gigabytes."""
    vm = psutil.virtual_memory()
    total_gb = round(vm.total / (1024 ** 3), 2)
    used_gb = round(vm.used / (1024 ** 3), 2)
    available_gb = round(vm.available / (1024 ** 3), 2)
    percent = vm.percent

    return {
        "total_gb": total_gb,
        "used_gb": used_gb,
        "available_gb": available_gb,
        "percent": percent
    }


def get_disk_metrics() -> Dict[str, Any]:
    """Retrieve primary secondary storage utilization in Gigabytes."""
    total_bytes = 0
    used_bytes = 0
    free_bytes = 0

    try:
        partitions = psutil.disk_partitions(all=False)
    except Exception:
        partitions = []

    for part in partitions:
        if "cdrom" in part.opts or part.fstype == "":
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_bytes += usage.total
            used_bytes += usage.used
            free_bytes += usage.free
        except (PermissionError, OSError, FileNotFoundError):
            continue

    if total_bytes > 0:
        total_gb = round(total_bytes / (1024 ** 3), 2)
        used_gb = round(used_bytes / (1024 ** 3), 2)
        free_gb = round(free_bytes / (1024 ** 3), 2)
        percent = round((used_bytes / total_bytes) * 100, 1)
    else:
        # Fallback to root if partition loop was empty
        try:
            usage = psutil.disk_usage("/")
            total_gb = round(usage.total / (1024 ** 3), 2)
            used_gb = round(usage.used / (1024 ** 3), 2)
            free_gb = round(usage.free / (1024 ** 3), 2)
            percent = usage.percent
        except Exception:
            total_gb, used_gb, free_gb, percent = 0.0, 0.0, 0.0, 0.0

    return {
        "total_gb": total_gb,
        "used_gb": used_gb,
        "free_gb": free_gb,
        "percent": percent
    }


def get_process_count() -> int:
    """Return total number of currently running system processes."""
    try:
        return len(psutil.pids())
    except Exception:
        return 0


def get_live_metrics_snapshot() -> Dict[str, Any]:
    """Capture a synchronized snapshot of all core system metrics."""
    return {
        "system": get_system_info(),
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics(),
        "process_count": get_process_count(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

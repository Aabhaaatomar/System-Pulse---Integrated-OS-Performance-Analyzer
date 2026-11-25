"""
SystemPulse - Alerts & Recommendations Module
Manages threshold configuration, threshold breach detection,
and data-driven recommendations linked to actual metrics.
"""

import os
import json
from typing import Dict, List, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")

DEFAULT_THRESHOLDS = {
    "cpu_threshold": 85.0,
    "memory_threshold": 85.0,
    "disk_threshold": 90.0
}


def load_thresholds() -> Dict[str, float]:
    """Load configurable thresholds from JSON or return defaults."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_FILE):
        save_thresholds(DEFAULT_THRESHOLDS)
        return DEFAULT_THRESHOLDS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "cpu_threshold": float(data.get("cpu_threshold", 85.0)),
                "memory_threshold": float(data.get("memory_threshold", 85.0)),
                "disk_threshold": float(data.get("disk_threshold", 90.0))
            }
    except Exception:
        save_thresholds(DEFAULT_THRESHOLDS)
        return DEFAULT_THRESHOLDS.copy()


def save_thresholds(thresholds: Dict[str, float]) -> bool:
    """Save validated thresholds to JSON file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    sanitized = {
        "cpu_threshold": max(10.0, min(99.0, float(thresholds.get("cpu_threshold", 85.0)))),
        "memory_threshold": max(10.0, min(99.0, float(thresholds.get("memory_threshold", 85.0)))),
        "disk_threshold": max(10.0, min(99.0, float(thresholds.get("disk_threshold", 90.0))))
    }
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, indent=4)
        return True
    except Exception:
        return False


def check_alerts(
    cpu_percent: float,
    ram_percent: float,
    disk_percent: float,
    thresholds: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Check if measured CPU, RAM, or Disk cross configured thresholds.
    Returns list of active alert objects.
    """
    alerts = []
    cpu_th = thresholds.get("cpu_threshold", 85.0)
    ram_th = thresholds.get("memory_threshold", 85.0)
    disk_th = thresholds.get("disk_threshold", 90.0)

    if cpu_percent >= cpu_th:
        alerts.append({
            "resource": "CPU",
            "measured": cpu_percent,
            "threshold": cpu_th,
            "severity": "CRITICAL" if cpu_percent >= 95.0 else "WARNING",
            "message": f"CPU usage is high at {cpu_percent:.1f}% (Threshold: {cpu_th:.1f}%)"
        })

    if ram_percent >= ram_th:
        alerts.append({
            "resource": "RAM",
            "measured": ram_percent,
            "threshold": ram_th,
            "severity": "CRITICAL" if ram_percent >= 95.0 else "WARNING",
            "message": f"Memory consumption elevated at {ram_percent:.1f}% (Threshold: {ram_th:.1f}%)"
        })

    if disk_percent >= disk_th:
        alerts.append({
            "resource": "Disk",
            "measured": disk_percent,
            "threshold": disk_th,
            "severity": "CRITICAL" if disk_percent >= 95.0 else "WARNING",
            "message": f"Disk space critical at {disk_percent:.1f}% (Threshold: {disk_th:.1f}%)"
        })

    return alerts


def generate_recommendations(
    cpu_percent: float,
    ram_percent: float,
    disk_percent: float,
    thresholds: Dict[str, float],
    processes: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate measurement-based OS recommendations.
    Identifies specific top CPU and memory hogging processes when elevated.
    """
    recommendations = []
    cpu_th = thresholds.get("cpu_threshold", 85.0)
    ram_th = thresholds.get("memory_threshold", 85.0)
    disk_th = thresholds.get("disk_threshold", 90.0)

    # 1. CPU Analysis
    if cpu_percent >= cpu_th:
        # Find culprit process
        user_procs = [p for p in processes if p["name"].lower() not in ["system idle process", "idle"] and p["pid"] != 0]
        user_procs.sort(key=lambda x: x["cpu_percent"], reverse=True)
        top_p = user_procs[0] if user_procs else None

        if top_p:
            recommendations.append({
                "type": "warning",
                "title": "High CPU Consumption Detected",
                "text": f"CPU is at {cpu_percent:.1f}%. The highest active process is '{top_p['name']}' (PID: {top_p['pid']}) consuming {top_p['cpu_percent']}%.",
                "action": "Consider lowering process priority or closing unused compute-heavy programs to free CPU cycles."
            })
        else:
            recommendations.append({
                "type": "warning",
                "title": "High CPU Consumption Detected",
                "text": f"Total CPU load is {cpu_percent:.1f}%, exceeding the {cpu_th:.1f}% threshold across multiple system tasks.",
                "action": "Inspect background tasks to prevent scheduling bottlenecks."
            })

    # 2. Memory Analysis
    if ram_percent >= ram_th:
        sorted_mem = sorted(processes, key=lambda x: x["memory_mb"], reverse=True)
        top_m = sorted_mem[0] if sorted_mem else None

        if top_m:
            recommendations.append({
                "type": "warning",
                "title": "High Memory Pressure Detected",
                "text": f"RAM usage is {ram_percent:.1f}%. Leading consumer is '{top_m['name']}' (PID: {top_m['pid']}) holding {top_m['memory_mb']:.1f} MB.",
                "action": "Close idle browser tabs or heavy background applications to prevent the OS from page swapping to disk."
            })
        else:
            recommendations.append({
                "type": "warning",
                "title": "Memory Capacity Alert",
                "text": f"RAM usage is at {ram_percent:.1f}%. Available memory headroom is critically constrained.",
                "action": "Free memory to avoid disk thrashing and high paging latency."
            })

    # 3. Disk Analysis
    if disk_percent >= disk_th:
        recommendations.append({
            "type": "warning",
            "title": "Low Storage Availability",
            "text": f"Storage volume is {disk_percent:.1f}% full (Threshold: {disk_th:.1f}%).",
            "action": "Delete temporary files or transfer large media to prevent write failures and virtual memory pagefile allocation errors."
        })

    # 4. Healthy State
    if not recommendations:
        recommendations.append({
            "type": "success",
            "title": "System Operating Nominally",
            "text": f"CPU ({cpu_percent:.1f}%), RAM ({ram_percent:.1f}%), and Disk ({disk_percent:.1f}%) are all within safe thresholds.",
            "action": "No immediate user action required. System resources are balanced and healthy."
        })

    return recommendations

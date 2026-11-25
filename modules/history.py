"""
SystemPulse - History Manager Module
Handles appending real-time system metrics to CSV and loading
historical telemetry into Pandas DataFrames for time-series visualization.
"""

import os
import csv
import time
import pandas as pd
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "system_history.csv")

CSV_COLUMNS = ["timestamp", "cpu_percent", "ram_percent", "ram_available_gb", "disk_percent", "process_count"]


def ensure_history_file() -> None:
    """Ensure data directory and history CSV file exist with correct headers."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)


def log_metrics(
    cpu_percent: float,
    ram_percent: float,
    ram_available_gb: float,
    disk_percent: float,
    process_count: int,
    max_rows: int = 500
) -> bool:
    """Append a telemetry snapshot row to the historical CSV log."""
    ensure_history_file()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    row = [
        now_str,
        round(cpu_percent, 1),
        round(ram_percent, 1),
        round(ram_available_gb, 2),
        round(disk_percent, 1),
        int(process_count)
    ]

    try:
        with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        # Keep file size bounded to max_rows
        _prune_history(max_rows)
        return True
    except Exception:
        return False


def _prune_history(max_rows: int) -> None:
    """Prune oldest records if CSV exceeds max_rows."""
    if not os.path.exists(HISTORY_FILE):
        return
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > max_rows + 1:
            header = lines[0]
            retained = lines[-(max_rows):]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write(header)
                f.writelines(retained)
    except Exception:
        pass


def get_history_df(limit: Optional[int] = None) -> pd.DataFrame:
    """Load historical metrics into a cleaned pandas DataFrame."""
    ensure_history_file()
    if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
        return pd.DataFrame(columns=CSV_COLUMNS)

    try:
        df = pd.read_csv(HISTORY_FILE)
        for col in CSV_COLUMNS:
            if col not in df.columns:
                df[col] = 0.0

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp"])

        for col in ["cpu_percent", "ram_percent", "ram_available_gb", "disk_percent", "process_count"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        df = df.sort_values(by="timestamp", ascending=True)
        if limit and limit > 0 and len(df) > limit:
            df = df.iloc[-limit:]

        return df.reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=CSV_COLUMNS)


def clear_history() -> bool:
    """Reset history file with empty headers."""
    ensure_history_file()
    try:
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_COLUMNS)
        return True
    except Exception:
        return False

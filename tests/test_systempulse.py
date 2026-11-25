"""
SystemPulse - Automated Unit Test Suite
Verifies all 4 Capstone Modules:
1. System Dashboard metrics (CPU, RAM, Disk, System Info)
2. Process Monitor (PID, names, memory, CPU, search, sort)
3. Performance History (CSV logging, DataFrame, CSV download)
4. Alerts & Recommendations (Thresholds, warning triggers, recommendations)
"""

import os
import sys
import unittest
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from modules.monitor import (
    get_system_info, get_cpu_metrics, get_memory_metrics,
    get_disk_metrics, get_process_count, get_live_metrics_snapshot, format_uptime
)
from modules.process import (
    get_all_processes, get_top_processes, search_and_sort_processes
)
from modules.history import (
    log_metrics, get_history_df, clear_history
)
from modules.alerts import (
    load_thresholds, save_thresholds, check_alerts, generate_recommendations
)


class TestSystemPulseCore(unittest.TestCase):

    # -------------------------------------------------------------
    # Module 1: System Dashboard Tests
    # -------------------------------------------------------------
    def test_01_system_info(self):
        """Verify host metadata and uptime formatting."""
        info = get_system_info()
        self.assertIn("hostname", info)
        self.assertIn("os_name", info)
        self.assertGreaterEqual(info["physical_cores"], 1)
        self.assertGreaterEqual(info["logical_cores"], 1)
        self.assertEqual(format_uptime(0), "0s")
        self.assertEqual(format_uptime(3665), "1h 1m 5s")

    def test_02_cpu_metrics(self):
        """Verify live CPU metrics."""
        cpu = get_cpu_metrics()
        self.assertGreaterEqual(cpu["total_percent"], 0.0)
        self.assertLessEqual(cpu["total_percent"], 100.0)
        self.assertIsInstance(cpu["per_core"], list)
        self.assertGreaterEqual(len(cpu["per_core"]), 1)

    def test_03_memory_and_disk_metrics(self):
        """Verify RAM and secondary storage metrics."""
        mem = get_memory_metrics()
        self.assertGreater(mem["total_gb"], 0.0)
        self.assertGreater(mem["used_gb"], 0.0)
        self.assertGreater(mem["available_gb"], 0.0)
        self.assertGreaterEqual(mem["percent"], 0.0)
        self.assertLessEqual(mem["percent"], 100.0)

        disk = get_disk_metrics()
        self.assertGreater(disk["total_gb"], 0.0)
        self.assertGreaterEqual(disk["percent"], 0.0)
        self.assertLessEqual(disk["percent"], 100.0)

        procs_cnt = get_process_count()
        self.assertGreater(procs_cnt, 0)

    # -------------------------------------------------------------
    # Module 2: Process Monitor Tests
    # -------------------------------------------------------------
    def test_04_process_enumeration(self):
        """Verify safe process enumeration without errors."""
        procs = get_all_processes()
        self.assertIsInstance(procs, list)
        self.assertGreater(len(procs), 0)

        p = procs[0]
        self.assertIn("pid", p)
        self.assertIn("name", p)
        self.assertIn("cpu_percent", p)
        self.assertIn("memory_mb", p)

    def test_05_process_search_and_sort(self):
        """Verify sorting and searching processes."""
        procs = get_all_processes()
        
        # Test sorting
        sorted_by_mem = search_and_sort_processes(procs, sort_by="memory_mb", ascending=False)
        if len(sorted_by_mem) >= 2:
            self.assertGreaterEqual(sorted_by_mem[0]["memory_mb"], sorted_by_mem[1]["memory_mb"])

        # Test top processes
        top_cpu = get_top_processes(procs, n=3, by="cpu")
        self.assertLessEqual(len(top_cpu), 3)

        top_mem = get_top_processes(procs, n=3, by="memory")
        self.assertLessEqual(len(top_mem), 3)

    # -------------------------------------------------------------
    # Module 3: Performance History Tests
    # -------------------------------------------------------------
    def test_06_history_logging_and_export(self):
        """Verify appending metrics to CSV and reading back."""
        success = log_metrics(15.5, 45.0, 8.2, 35.0, 120)
        self.assertTrue(success)

        df = get_history_df()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty)
        self.assertIn("cpu_percent", df.columns)
        self.assertIn("ram_percent", df.columns)

    # -------------------------------------------------------------
    # Module 4: Alerts and System Analysis Tests
    # -------------------------------------------------------------
    def test_07_threshold_save_and_load(self):
        """Verify threshold persistence and bounds clamping."""
        test_th = {"cpu_threshold": 92.0, "memory_threshold": 80.0, "disk_threshold": 88.0}
        self.assertTrue(save_thresholds(test_th))

        loaded = load_thresholds()
        self.assertEqual(loaded["cpu_threshold"], 92.0)
        self.assertEqual(loaded["memory_threshold"], 80.0)
        self.assertEqual(loaded["disk_threshold"], 88.0)

    def test_08_alert_triggering(self):
        """Verify threshold breach alert generation."""
        low_th = {"cpu_threshold": 10.0, "memory_threshold": 10.0, "disk_threshold": 10.0}
        alerts = check_alerts(cpu_percent=50.0, ram_percent=50.0, disk_percent=50.0, thresholds=low_th)
        self.assertEqual(len(alerts), 3)

    def test_09_recommendations_culprit_detection(self):
        """Verify culprit identification in high usage state."""
        mock_procs = [
            {"pid": 9999, "name": "heavy_compiler", "cpu_percent": 90.0, "memory_mb": 4096.0, "memory_percent": 25.0, "status": "running"}
        ]
        high_th = {"cpu_threshold": 70.0, "memory_threshold": 70.0, "disk_threshold": 70.0}
        recs = generate_recommendations(85.0, 85.0, 50.0, high_th, mock_procs)
        
        self.assertTrue(len(recs) >= 2)
        rec_text = " ".join([r["text"] for r in recs])
        self.assertIn("heavy_compiler", rec_text)


if __name__ == "__main__":
    unittest.main()

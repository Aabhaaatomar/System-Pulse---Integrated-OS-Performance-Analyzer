"""
SystemPulse - Project Launcher
Simple one-click launcher for the SystemPulse dashboard.
Usage:
    python run.py
"""

import os
import sys
import subprocess

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    app_file = os.path.join(project_dir, "app.py")

    print("=" * 65)
    print("  SystemPulse — Integrated OS Performance Analyzer")
    print("  Operating Systems Capstone Project (B.Tech CSE)")
    print("=" * 65)
    print(f"Launching dashboard at http://localhost:8501 ...")
    print("Press Ctrl+C to terminate.\n")

    # Set environment variables to avoid Streamlit onboarding prompt
    env = os.environ.copy()
    env["USERPROFILE"] = project_dir
    env["HOME"] = project_dir
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    cmd = [
        sys.executable, "-m", "streamlit", "run", app_file,
        "--server.port", "8501",
        "--server.headless", "false",
        "--browser.gatherUsageStats", "false"
    ]

    try:
        subprocess.run(cmd, cwd=project_dir, env=env)
    except KeyboardInterrupt:
        print("\n[INFO] SystemPulse terminated gracefully.")

if __name__ == "__main__":
    main()

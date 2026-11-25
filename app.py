"""
=============================================================================
SystemPulse — Integrated OS Performance Analyzer
B.Tech CSE Operating Systems Capstone Project
=============================================================================
A modern, real-time operating system performance analyzer and process monitoring
dashboard demonstrating core OS concepts using Python, Streamlit, psutil, Plotly & Pandas.
"""

import os
import sys
import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from modules.monitor import get_live_metrics_snapshot
from modules.process import get_all_processes, get_top_processes, search_and_sort_processes
from modules.history import log_metrics, get_history_df, clear_history
from modules.alerts import load_thresholds, save_thresholds, check_alerts, generate_recommendations


# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Dark Theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SystemPulse — OS Performance Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
css_file = os.path.join(PROJECT_ROOT, "assets", "style.css")
if os.path.exists(css_file):
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def get_status_color(val: float, thresh: float) -> str:
    """Return color based on value vs threshold."""
    if val >= thresh:
        return "#EF4444"  # Red
    elif val >= thresh - 15.0:
        return "#F59E0B"  # Amber
    return "#22C55E"      # Green


def render_metric_card(title: str, value: str, sub: str, percent: float, thresh: float, icon: str):
    """Render a modern dark metric card with badge and progress bar."""
    color = get_status_color(percent, thresh)
    badge_text = "CRITICAL" if percent >= thresh else ("ELEVATED" if percent >= thresh - 15.0 else "NORMAL")
    badge_class = "badge-danger" if percent >= thresh else ("badge-warning" if percent >= thresh - 15.0 else "badge-success")
    clamped_p = max(0.0, min(100.0, percent))

    card_html = f"""
    <div class="metric-card" style="border-top: 3px solid {color};">
        <div class="metric-header">
            <span class="metric-title">{title}</span>
            <div>
                <span class="badge {badge_class}">{badge_text}</span>
                <span style="margin-left: 6px;">{icon}</span>
            </div>
        </div>
        <div class="metric-val" style="color: {'#EF4444' if percent >= thresh else '#FFFFFF'};">{value}</div>
        <div class="pulse-prog-bg">
            <div class="pulse-prog-fill" style="width: {clamped_p}%; background: {color};"></div>
        </div>
        <div class="metric-sub">{sub}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


def get_plotly_layout(title: str = "", height: int = 320):
    """Return standard dark theme dictionary for Plotly charts."""
    return {
        "title": {"text": title, "font": {"size": 13, "color": "#E5E7EB"}},
        "paper_bgcolor": "rgba(17, 24, 39, 0)",
        "plot_bgcolor": "rgba(17, 24, 39, 0.4)",
        "margin": {"l": 35, "r": 20, "t": 40, "b": 30},
        "height": height,
        "font": {"family": "Plus Jakarta Sans, sans-serif", "color": "#9CA3AF"},
        "xaxis": {"gridcolor": "#1F2937", "linecolor": "#374151"},
        "yaxis": {"gridcolor": "#1F2937", "linecolor": "#374151"},
        "legend": {"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1}
    }


# -----------------------------------------------------------------------------
# 2. Collect Real Operating System Telemetry
# -----------------------------------------------------------------------------
thresholds = load_thresholds()
snapshot = get_live_metrics_snapshot()
processes = get_all_processes()

cpu_val = snapshot["cpu"]["total_percent"]
ram_val = snapshot["memory"]["percent"]
ram_avail = snapshot["memory"]["available_gb"]
disk_val = snapshot["disk"]["percent"]
proc_cnt = snapshot["process_count"]
sys_info = snapshot["system"]

# Check active alerts
active_alerts = check_alerts(cpu_val, ram_val, disk_val, thresholds)

# Log to history CSV
log_metrics(cpu_val, ram_val, ram_avail, disk_val, proc_cnt)
history_df = get_history_df(limit=100)


# -----------------------------------------------------------------------------
# 3. Sidebar: Configuration & Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.8rem 0; border-bottom: 1px solid #1E293B; margin-bottom: 1rem;">
        <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF;">
            ⚡ <span style="background: linear-gradient(135deg, #6366F1, #06B6D4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">SystemPulse</span>
        </div>
        <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">
            OS Performance Analyzer
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Live Vitals Summary Box
    st.markdown(f"""
    <div style="background: #111827; border: 1px solid #1F2937; border-radius: 8px; padding: 0.8rem; margin-bottom: 1.2rem;">
        <div style="font-size: 0.72rem; text-transform: uppercase; color: #9CA3AF; font-weight: 700; margin-bottom: 6px;">Live Vitals</div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 3px;">
            <span style="color: #9CA3AF;">CPU Load:</span>
            <strong style="color: {get_status_color(cpu_val, thresholds['cpu_threshold'])};">{cpu_val}%</strong>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 3px;">
            <span style="color: #9CA3AF;">RAM Load:</span>
            <strong style="color: {get_status_color(ram_val, thresholds['memory_threshold'])};">{ram_val}%</strong>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 3px;">
            <span style="color: #9CA3AF;">Disk Load:</span>
            <strong style="color: {get_status_color(disk_val, thresholds['disk_threshold'])};">{disk_val}%</strong>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.82rem;">
            <span style="color: #9CA3AF;">Active Alerts:</span>
            <strong style="color: {'#EF4444' if active_alerts else '#22C55E'};">{len(active_alerts)}</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Threshold Configuration Form
    st.markdown("<h4 style='font-size: 0.95rem; color: #E5E7EB; margin-bottom: 0.5rem;'>⚙️ Alert Thresholds</h4>", unsafe_allow_html=True)
    with st.form("threshold_form"):
        new_cpu_th = st.slider("CPU Threshold (%)", 10, 99, int(thresholds["cpu_threshold"]), step=1)
        new_ram_th = st.slider("RAM Threshold (%)", 10, 99, int(thresholds["memory_threshold"]), step=1)
        new_disk_th = st.slider("Disk Threshold (%)", 10, 99, int(thresholds["disk_threshold"]), step=1)
        
        save_btn = st.form_submit_button("Save Thresholds", use_container_width=True)
        if save_btn:
            save_thresholds({
                "cpu_threshold": float(new_cpu_th),
                "memory_threshold": float(new_ram_th),
                "disk_threshold": float(new_disk_th)
            })
            st.success("Thresholds updated!")
            st.rerun()

    st.markdown("<hr style='border-color: #1E293B; margin: 1rem 0;'>", unsafe_allow_html=True)

    # Telemetry Refresh Controls
    st.markdown("<h4 style='font-size: 0.95rem; color: #E5E7EB; margin-bottom: 0.5rem;'>⏱️ Sampling Controls</h4>", unsafe_allow_html=True)
    auto_refresh = st.checkbox("Live Auto-Refresh", value=True)
    refresh_sec = st.selectbox("Interval", options=[2, 3, 5, 10], index=1, format_func=lambda s: f"{s} seconds")

    if st.button("🔄 Refresh Telemetry Now", use_container_width=True):
        st.rerun()

    st.markdown(f"""
    <div style="font-size: 0.72rem; color: #6B7280; text-align: center; margin-top: 1rem;">
        Last Sampled: {snapshot['timestamp'].split(' ')[1]}<br>
        B.Tech CSE Capstone Project
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. Host Metadata Banner
# -----------------------------------------------------------------------------
st.markdown(f"""
<div style="background: #111827; border: 1px solid #1F2937; border-radius: 10px; padding: 0.9rem 1.2rem; margin-bottom: 1.2rem; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.8rem;">
    <div>
        <div style="font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">
            🖥️ Host: <span style="color: #6366F1;">{sys_info['hostname']}</span>
        </div>
        <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 2px;">
            {sys_info['os_name']} {sys_info['os_release']} ({sys_info['architecture']}) &bull; {sys_info['processor']}
        </div>
    </div>
    <div style="display: flex; gap: 1.5rem;">
        <div>
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #6B7280; font-weight: 600;">Uptime</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #10B981;">{sys_info['uptime_formatted']}</div>
        </div>
        <div>
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #6B7280; font-weight: 600;">Cores (P/L)</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #38BDF8;">{sys_info['physical_cores']}P / {sys_info['logical_cores']}L</div>
        </div>
        <div>
            <div style="font-size: 0.72rem; text-transform: uppercase; color: #6B7280; font-weight: 600;">Clock</div>
            <div style="font-size: 0.95rem; font-weight: 700; color: #F59E0B;">{snapshot['cpu']['freq_mhz']} MHz</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 5. Four Core Application Tabs (Directly Matching the 4 Capstone Modules)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 System Dashboard",
    "⚙️ Process Monitor",
    "📈 Performance Visualization",
    "🚨 Alerts & System Analysis"
])


# =============================================================================
# TAB 1: SYSTEM DASHBOARD (Module 1)
# =============================================================================
with tab1:
    st.markdown("<h4 style='color: #F3F4F6; margin-bottom: 0.8rem;'>Real-Time Operating System Vitals</h4>", unsafe_allow_html=True)
    
    # 4 Metric Cards
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric_card(
            title="CPU Utilization",
            value=f"{cpu_val}%",
            sub=f"Threshold: {thresholds['cpu_threshold']}%",
            percent=cpu_val,
            thresh=thresholds['cpu_threshold'],
            icon="⚡"
        )

    with c2:
        mem_info = snapshot["memory"]
        render_metric_card(
            title="RAM Utilization",
            value=f"{ram_val}%",
            sub=f"Used: {mem_info['used_gb']} GB | Avail: {mem_info['available_gb']} GB",
            percent=ram_val,
            thresh=thresholds['memory_threshold'],
            icon="🧠"
        )

    with c3:
        disk_info = snapshot["disk"]
        render_metric_card(
            title="Disk Utilization",
            value=f"{disk_val}%",
            sub=f"Used: {disk_info['used_gb']} GB / {disk_info['total_gb']} GB",
            percent=disk_val,
            thresh=thresholds['disk_threshold'],
            icon="💾"
        )

    with c4:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 3px solid #6366F1;">
            <div class="metric-header">
                <span class="metric-title">Running Processes</span>
                <span style="font-size: 1.1rem;">⚙️</span>
            </div>
            <div class="metric-val">{proc_cnt}</div>
            <div class="pulse-prog-bg">
                <div class="pulse-prog-fill" style="width: 100%; background: #6366F1;"></div>
            </div>
            <div class="metric-sub">Active kernel tasks in process table</div>
        </div>
        """, unsafe_allow_html=True)

    # Subsystem Visual Gauges & Allocations
    st.markdown("<h4 style='color: #F3F4F6; margin-top: 1rem;'>Subsystem Allocation Breakdown</h4>", unsafe_allow_html=True)
    g1, g2 = st.columns(2)

    with g1:
        # RAM Donut Chart
        mem_labels = ['Used RAM', 'Available RAM']
        mem_values = [mem_info['used_gb'], mem_info['available_gb']]
        fig_mem = go.Figure(data=[go.Pie(
            labels=mem_labels,
            values=mem_values,
            hole=0.6,
            marker_colors=['#6366F1', '#10B981'],
            textinfo='label+percent'
        )])
        layout_m = get_plotly_layout(f"Physical Memory Pool (Total: {mem_info['total_gb']} GB)", height=240)
        fig_mem.update_layout(layout_m)
        st.plotly_chart(fig_mem, use_container_width=True)

    with g2:
        # Disk Donut Chart
        disk_labels = ['Used Space', 'Free Space']
        disk_values = [disk_info['used_gb'], disk_info['free_gb']]
        fig_disk = go.Figure(data=[go.Pie(
            labels=disk_labels,
            values=disk_values,
            hole=0.6,
            marker_colors=['#F59E0B', '#38BDF8'],
            textinfo='label+percent'
        )])
        layout_d = get_plotly_layout(f"Storage Allocation (Total: {disk_info['total_gb']} GB)", height=240)
        fig_disk.update_layout(layout_d)
        st.plotly_chart(fig_disk, use_container_width=True)

    # Viva Concept Callout
    st.markdown("""
    <div class="viva-box">
        <strong>💡 OS Concept — Multiprogramming & Kernel Telemetry:</strong><br>
        The operating system dynamically allocates CPU time slices to active processes while balancing physical page frames between active working sets and file buffer caches. "Available RAM" represents physical frames immediately allocatable without invoking disk page swapping.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 2: PROCESS MONITOR (Module 2)
# =============================================================================
with tab2:
    st.markdown("<h4 style='color: #F3F4F6; margin-bottom: 0.8rem;'>Process Table & Top Resource Consumers</h4>", unsafe_allow_html=True)

    # Top Consumers Charts
    top_cpu = get_top_processes(processes, n=5, by="cpu")
    top_mem = get_top_processes(processes, n=5, by="memory")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if top_cpu:
            p_names = [f"{p['name']} ({p['pid']})" for p in reversed(top_cpu)]
            p_vals = [p["cpu_percent"] for p in reversed(top_cpu)]
            fig_top_c = go.Figure(go.Bar(
                x=p_vals, y=p_names, orientation='h',
                marker_color='#6366F1',
                text=[f"{v}%" for v in p_vals], textposition='auto'
            ))
            layout_tc = get_plotly_layout("Top 5 CPU-Consuming Processes (%)", height=220)
            layout_tc["xaxis"]["title"] = "CPU %"
            fig_top_c.update_layout(layout_tc)
            st.plotly_chart(fig_top_c, use_container_width=True)

    with col_t2:
        if top_mem:
            m_names = [f"{p['name']} ({p['pid']})" for p in reversed(top_mem)]
            m_vals = [p["memory_mb"] for p in reversed(top_mem)]
            fig_top_m = go.Figure(go.Bar(
                x=m_vals, y=m_names, orientation='h',
                marker_color='#10B981',
                text=[f"{v} MB" for v in m_vals], textposition='auto'
            ))
            layout_tm = get_plotly_layout("Top 5 Memory-Consuming Processes (MB)", height=220)
            layout_tm["xaxis"]["title"] = "Memory (MB)"
            fig_top_m.update_layout(layout_tm)
            st.plotly_chart(fig_top_m, use_container_width=True)

    # Search and Sort Controls
    st.markdown("<h4 style='color: #F3F4F6; margin-top: 0.8rem;'>Search & Sort Process List</h4>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns([2, 1, 1])

    with f1:
        search_query = st.text_input("🔍 Search Process by Name or PID", value="", placeholder="e.g. chrome, python, 1234")

    with f2:
        sort_choice = st.selectbox(
            "Sort Column",
            options=["CPU %", "Memory (MB)", "Memory %", "PID", "Process Name"],
            index=0
        )
        sort_map = {
            "CPU %": "cpu_percent",
            "Memory (MB)": "memory_mb",
            "Memory %": "memory_percent",
            "PID": "pid",
            "Process Name": "name"
        }
        sort_col = sort_map[sort_choice]

    with f3:
        sort_order = st.selectbox("Order", ["Descending", "Ascending"], index=0)
        is_asc = (sort_order == "Ascending")

    # Filtered Process Table
    filtered_procs = search_and_sort_processes(
        processes,
        query=search_query,
        sort_by=sort_col,
        ascending=is_asc
    )

    if filtered_procs:
        df_proc = pd.DataFrame(filtered_procs[:60])
        df_proc = df_proc[["pid", "name", "cpu_percent", "memory_mb", "memory_percent", "status"]]
        df_proc.columns = ["PID", "Process Name", "CPU (%)", "Memory (MB)", "Memory (%)", "State"]

        st.dataframe(
            df_proc,
            use_container_width=True,
            height=340,
            column_config={
                "PID": st.column_config.NumberColumn(format="%d"),
                "CPU (%)": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
                "Memory (MB)": st.column_config.NumberColumn(format="%.1f MB"),
                "Memory (%)": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100)
            }
        )
        st.caption(f"Showing top {min(len(df_proc), 60)} matching processes (Total running: {len(processes)}). Safe read-only mode.")
    else:
        st.info("No active processes match your search filter.")

    # Viva Concept Callout
    st.markdown("""
    <div class="viva-box">
        <strong>💡 OS Concept — Process Control Block (PCB):</strong><br>
        Each running process is tracked by the kernel using a PCB that records its PID, register states, execution state (running, sleeping, zombie), page tables, and memory usage. SystemPulse safely inspects PCB attributes without modifying process state.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 3: PERFORMANCE VISUALIZATION (Module 3)
# =============================================================================
with tab3:
    st.markdown("<h4 style='color: #F3F4F6; margin-bottom: 0.8rem;'>Historical Telemetry Graphs</h4>", unsafe_allow_html=True)

    if not history_df.empty:
        # Time-Series: CPU and RAM over time
        p1, p2 = st.columns(2)

        with p1:
            fig_cpu_hist = go.Figure()
            fig_cpu_hist.add_trace(go.Scatter(
                x=history_df["timestamp"], y=history_df["cpu_percent"],
                mode="lines", name="CPU (%)",
                line=dict(color="#6366F1", width=2.5),
                fill="tozeroy", fillcolor="rgba(99, 102, 241, 0.15)"
            ))
            fig_cpu_hist.add_hline(
                y=thresholds["cpu_threshold"], line_dash="dash", line_color="#EF4444",
                annotation_text=f"Threshold ({thresholds['cpu_threshold']}%)",
                annotation_position="top right", annotation_font_color="#EF4444"
            )
            layout_ch = get_plotly_layout("CPU Utilization Over Time (%)", height=280)
            layout_ch["yaxis"]["range"] = [0, 100]
            fig_cpu_hist.update_layout(layout_ch)
            st.plotly_chart(fig_cpu_hist, use_container_width=True)

        with p2:
            fig_ram_hist = go.Figure()
            fig_ram_hist.add_trace(go.Scatter(
                x=history_df["timestamp"], y=history_df["ram_percent"],
                mode="lines", name="RAM (%)",
                line=dict(color="#10B981", width=2.5),
                fill="tozeroy", fillcolor="rgba(16, 185, 129, 0.15)"
            ))
            fig_ram_hist.add_hline(
                y=thresholds["memory_threshold"], line_dash="dash", line_color="#EF4444",
                annotation_text=f"Threshold ({thresholds['memory_threshold']}%)",
                annotation_position="top right", annotation_font_color="#EF4444"
            )
            layout_rh = get_plotly_layout("RAM Utilization Over Time (%)", height=280)
            layout_rh["yaxis"]["range"] = [0, 100]
            fig_ram_hist.update_layout(layout_rh)
            st.plotly_chart(fig_ram_hist, use_container_width=True)

        # Multi-Resource Comparison Chart
        st.markdown("<h4 style='color: #F3F4F6; margin-top: 0.8rem;'>Synchronized Resource Comparison</h4>", unsafe_allow_html=True)
        fig_multi = go.Figure()
        fig_multi.add_trace(go.Scatter(x=history_df["timestamp"], y=history_df["cpu_percent"], name="CPU (%)", line=dict(color="#6366F1", width=2)))
        fig_multi.add_trace(go.Scatter(x=history_df["timestamp"], y=history_df["ram_percent"], name="RAM (%)", line=dict(color="#10B981", width=2)))
        fig_multi.add_trace(go.Scatter(x=history_df["timestamp"], y=history_df["disk_percent"], name="Disk (%)", line=dict(color="#F59E0B", width=2)))
        layout_m = get_plotly_layout("Resource Comparison Timeline (%)", height=300)
        layout_m["yaxis"]["range"] = [0, 100]
        fig_multi.update_layout(layout_m)
        st.plotly_chart(fig_multi, use_container_width=True)

        # Historical Table & CSV Export
        st.markdown("<h4 style='color: #F3F4F6; margin-top: 0.8rem;'>Telemetry History Table (CSV)</h4>", unsafe_allow_html=True)
        display_hist = history_df.sort_values(by="timestamp", ascending=False).copy()
        display_hist["timestamp"] = display_hist["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        st.dataframe(display_hist, use_container_width=True, height=220)

        col_dl, col_cl = st.columns([1, 1])
        with col_dl:
            csv_bytes = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Telemetry Log (CSV)",
                data=csv_bytes,
                file_name="systempulse_history.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_cl:
            if st.button("🗑️ Clear Historical Log", use_container_width=True):
                clear_history()
                st.success("Historical data cleared.")
                st.rerun()
    else:
        st.info("Accumulating performance history... Charts will populate after initial refresh cycles.")

    # Viva Concept Callout
    st.markdown("""
    <div class="viva-box">
        <strong>💡 OS Concept — Capacity Planning & Resource Accounting:</strong><br>
        Periodic time-series accounting is essential to spot memory leaks (gradual monotonic growth in RAM) and detect sustained CPU saturation that leads to dispatch queue starvation.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# TAB 4: ALERTS & SYSTEM ANALYSIS (Module 4)
# =============================================================================
with tab4:
    st.markdown("<h4 style='color: #F3F4F6; margin-bottom: 0.8rem;'>Alert Violations & Measurement-Based Recommendations</h4>", unsafe_allow_html=True)

    # 1. Active Alerts Section
    st.markdown("<h5 style='color: #E5E7EB;'>Active Threshold Alerts</h5>", unsafe_allow_html=True)
    if active_alerts:
        for alert in active_alerts:
            sev = alert["severity"]
            is_crit = sev == "CRITICAL"
            st.markdown(f"""
            <div class="rec-card rec-card-warning" style="border-left-color: {'#EF4444' if is_crit else '#F59E0B'};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong style="color: #FFFFFF; font-size: 1rem;">⚠️ {alert['resource']} Threshold Breach</strong>
                    <span class="badge {'badge-danger' if is_crit else 'badge-warning'}">{sev}</span>
                </div>
                <div style="color: #E5E7EB; font-size: 0.9rem; margin-top: 4px;">
                    {alert['message']}
                </div>
                <div style="color: #9CA3AF; font-size: 0.8rem; margin-top: 3px;">
                    Current: <strong>{alert['measured']:.1f}%</strong> | Configured Limit: <strong>{alert['threshold']:.1f}%</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="rec-card rec-card-success">
            <strong style="color: #4ADE80; font-size: 0.95rem;">✅ All Subsystems Normal</strong>
            <p style="color: #A7F3D0; font-size: 0.85rem; margin-top: 3px; margin-bottom: 0;">
                CPU, Memory, and Storage utilization are well below their configured thresholds.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 2. Measurement-Based System Recommendations
    st.markdown("<h5 style='color: #E5E7EB; margin-top: 1rem;'>Intelligent OS Recommendations</h5>", unsafe_allow_html=True)
    recommendations = generate_recommendations(cpu_val, ram_val, disk_val, thresholds, processes)

    for rec in recommendations:
        card_class = "rec-card-warning" if rec["type"] == "warning" else "rec-card-success"
        badge_class = "badge-warning" if rec["type"] == "warning" else "badge-success"
        badge_text = "RECOMMENDATION" if rec["type"] == "warning" else "HEALTHY"

        st.markdown(f"""
        <div class="rec-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="color: #FFFFFF; font-size: 0.95rem;">{rec['title']}</strong>
                <span class="badge {badge_class}">{badge_text}</span>
            </div>
            <div style="color: #D1D5DB; font-size: 0.88rem; margin-top: 5px; line-height: 1.4;">
                {rec['text']}
            </div>
            <div style="background: #0B1120; border-radius: 6px; padding: 0.5rem 0.8rem; margin-top: 8px; font-size: 0.8rem; color: #94A3B8; border: 1px solid #1E293B;">
                <strong style="color: #818CF8;">Suggested Action:</strong> {rec['action']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Viva Concept Callout
    st.markdown("""
    <div class="viva-box">
        <strong>💡 OS Concept — Threshold Traps & Bottleneck Mitigation:</strong><br>
        Operating system monitors detect resource saturation (such as thrashing or scheduler queue starvation) and generate signals (e.g. SIGXCPU) or trigger page reclamation routines. Dynamic recommendations map directly to OS remedies such as adjusting process niceness or reclaiming inactive page buffers.
    </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 6. Global Footer & Auto-Refresh Timing
# -----------------------------------------------------------------------------
st.markdown("""
<div style="text-align: center; color: #4B5563; font-size: 0.75rem; padding: 1.5rem 0 0.5rem 0; border-top: 1px solid #1F2937; margin-top: 2rem;">
    <strong>SystemPulse</strong> — Integrated OS Performance Analyzer &bull; Built with Python, Streamlit, psutil, Plotly & Pandas
</div>
""", unsafe_allow_html=True)

if auto_refresh:
    time.sleep(refresh_sec)
    st.rerun()

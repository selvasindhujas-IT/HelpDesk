"""
pages/diagnostics.py
-----------------------
System Diagnostics page: displays live system information and lets the user
trigger safe, predefined diagnostic tools via buttons.
"""

import streamlit as st

from config.config import Config
from tools import system_tools

st.set_page_config(page_title="System Diagnostics", page_icon="🛠️", layout="wide")

st.title("🛠️ System Diagnostics")
st.caption("Live system information gathered using safe, predefined diagnostic tools only.")

if Config.DEMO_MODE:
    st.info("🟡 Demo Mode is active for the LLM, but diagnostics below run live on this machine.")

st.divider()

st.markdown("### 📋 Quick Overview")

col1, col2, col3 = st.columns(3)

with st.spinner("Gathering system overview..."):
    sys_info = system_tools.get_system_information()
    hostname_info = system_tools.get_hostname()
    ip_info = system_tools.get_local_ip()
    cpu_info = system_tools.get_cpu_usage()
    mem_info = system_tools.get_memory_usage()
    disk_info = system_tools.get_disk_usage()

with col1:
    st.metric("Operating System", f"{sys_info.get('os', 'N/A')} {sys_info.get('os_release', '')}")
    st.metric("Hostname", hostname_info.get("hostname", "N/A"))

with col2:
    st.metric("Local IP Address", ip_info.get("local_ip", "N/A"))
    st.metric("CPU Usage", f"{cpu_info.get('cpu_usage_percent', 'N/A')}%")

with col3:
    st.metric("Memory Usage", f"{mem_info.get('memory_usage_percent', 'N/A')}%")
    st.metric("Disk Usage", f"{disk_info.get('disk_usage_percent', 'N/A')}%")

st.divider()
st.markdown("### 🔍 Run Individual Diagnostic Checks")

btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

with btn_col1:
    if st.button("🌐 Check Internet", use_container_width=True):
        with st.spinner("Checking internet connectivity..."):
            result = system_tools.check_internet_connection()
        if result.get("status") == "success":
            if result["internet_connected"]:
                st.success("✅ Internet connection is active.")
            else:
                st.error("❌ No internet connection detected.")
        else:
            st.warning(f"Could not complete check: {result.get('message')}")

with btn_col2:
    if st.button("🧭 Check DNS", use_container_width=True):
        with st.spinner("Checking DNS resolution..."):
            result = system_tools.check_dns_resolution()
        if result.get("status") == "success":
            if result["dns_working"]:
                st.success(f"✅ DNS is working (resolved {result['resolved_host']} → {result['resolved_ip']}).")
            else:
                st.error(f"❌ DNS resolution failed for {result['resolved_host']}.")
        else:
            st.warning(f"Could not complete check: {result.get('message')}")

with btn_col3:
    if st.button("💻 System Information", use_container_width=True):
        with st.spinner("Gathering system information..."):
            result = system_tools.get_system_information()
        if result.get("status") == "success":
            st.json(result)
        else:
            st.warning(f"Could not complete check: {result.get('message')}")

with btn_col4:
    if st.button("⚡ Performance Check", use_container_width=True):
        with st.spinner("Checking performance metrics..."):
            cpu = system_tools.get_cpu_usage()
            mem = system_tools.get_memory_usage()
            disk = system_tools.get_disk_usage()
        st.json({"cpu": cpu, "memory": mem, "disk": disk})

st.divider()
st.markdown("### 📡 Ping Test")
if st.button(f"Ping {Config.PING_TARGET_HOST}"):
    with st.spinner("Pinging..."):
        result = system_tools.ping_public_host()
    if result.get("status") == "success":
        if result["reachable"]:
            st.success(f"✅ {result['target']} is reachable.")
        else:
            st.error(f"❌ {result['target']} is not reachable.")
        with st.expander("Raw ping output"):
            st.code(result.get("output", ""))
    else:
        st.warning(f"Could not complete ping: {result.get('message')}")

st.divider()
st.caption(
    "🔒 Security note: only predefined, read-only diagnostic functions are executed here. "
    "No arbitrary commands, file deletions, or credential access are ever performed."
)

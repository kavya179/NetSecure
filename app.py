"""
NetSecure: Enterprise Network Design & Security Dashboard
Cisco Packet Tracer Companion & Network Operations Center (NOC) Dashboard
Built with Python, Streamlit, Pandas, and Matplotlib.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Import custom modular helpers
import data_manager
import topology_graph
import cisco_helpers

# -----------------------------------------------------------------------------
# STREAMLIT APP CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NetSecure | Enterprise Network Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
data_manager.init_session_state()

# -----------------------------------------------------------------------------
# CUSTOM CSS STYLING (DARK NAVY NOC THEME)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark Navy NOC Theme Palette */
    :root {
        --bg-main: #0B1120;
        --bg-card: #111A2E;
        --bg-card-hover: #16223B;
        --border-color: #1E293B;
        --border-highlight: #334155;
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --cyan-accent: #06B6D4;
        --blue-accent: #38BDF8;
        --green-status: #10B981;
        --yellow-status: #F59E0B;
        --red-status: #EF4444;
        --purple-dept: #A855F7;
        --yellow-dept: #EAB308;
        --pink-dept: #EC4899;
    }

    /* Overall Background and Base Text */
    .stApp {
        background-color: var(--bg-main);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Custom Header Container */
    .noc-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }

    .noc-title {
        font-size: 24px;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .noc-subtitle {
        font-size: 13px;
        color: var(--cyan-accent);
        margin: 4px 0 0 0;
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    .noc-badge {
        background: rgba(6, 182, 212, 0.12);
        color: var(--cyan-accent);
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* KPI Metric Cards */
    .metric-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 18px 20px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    .metric-card:hover {
        border-color: var(--cyan-accent);
        background-color: var(--bg-card-hover);
        transform: translateY(-2px);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 11.5px;
        color: var(--text-secondary);
        margin-top: 6px;
    }

    /* Disclaimer & Notice Banner */
    .disclaimer-banner {
        background: rgba(15, 23, 42, 0.8);
        border-left: 4px solid var(--yellow-status);
        border-top: 1px solid var(--border-color);
        border-right: 1px solid var(--border-color);
        border-bottom: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 20px;
        font-size: 12.5px;
        color: #E2E8F0;
        display: flex;
        align-items: flex-start;
        gap: 10px;
    }

    .disclaimer-title {
        font-weight: 700;
        color: var(--yellow-status);
        margin-bottom: 2px;
    }

    /* Department Cards */
    .dept-card {
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
        background-color: #111A2E;
        border: 1px solid var(--border-color);
    }
    .dept-card-purple { border-top: 4px solid var(--purple-dept); }
    .dept-card-yellow { border-top: 4px solid var(--yellow-dept); }
    .dept-card-pink   { border-top: 4px solid var(--pink-dept); }

    .dept-title {
        font-size: 15px;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Status Pills */
    .status-pill {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }
    .status-passed {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    .status-untested {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .status-failed {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }

    /* Custom Streamlit component adjustments */
    div[data-testid="stSidebarNav"] { display: none; }
    .stButton>button {
        background-color: #1E293B;
        color: #F8FAFC;
        border: 1px solid #334155;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: var(--cyan-accent);
        color: var(--cyan-accent);
        background-color: #16223B;
    }
    .stDownloadButton>button {
        background-color: #0369A1;
        color: #FFFFFF;
        border: 1px solid #38BDF8;
        border-radius: 8px;
        font-weight: 600;
    }
    .stDownloadButton>button:hover {
        background-color: #0284C7;
        border-color: #7DD3FC;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION & NOC TELEMETRY SUMMARY
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 20px 0; border-bottom: 1px solid #1E293B;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #06B6D4, #3B82F6); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 900; color: #0B1120;">
                    🛡️
                </div>
                <div>
                    <div style="font-size: 17px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px;">NetSecure</div>
                    <div style="font-size: 10px; color: #06B6D4; letter-spacing: 0.8px; font-weight: 700;">NOC DASHBOARD</div>
                </div>
            </div>
            <div style="margin-top: 12px; font-size: 11.5px; color: #94A3B8; line-height: 1.4;">
                Enterprise Network Design & Security Companion for Cisco Packet Tracer
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 10.5px; font-weight: 700; color: #64748B; letter-spacing: 1.2px; margin: 18px 0 8px 4px;'>NAVIGATION</p>", unsafe_allow_html=True)
    
    pages = [
        "📊 1. Overview & Health",
        "🗺️ 2. Network Topology",
        "🌐 3. VLAN & IP Addressing",
        "🔒 4. Security Policy & ACL",
        "🧪 5. Validation & Test Logs"
    ]
    
    # Check if page was set in session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = pages[0]

    selected_page = st.radio(
        "Navigate to Page",
        pages,
        index=pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0,
        label_visibility="collapsed"
    )
    st.session_state.current_page = selected_page

    st.markdown("---")

    # Quick Verification Health Gauge in Sidebar
    stats = data_manager.get_test_stats()
    st.markdown("<p style='font-size: 10.5px; font-weight: 700; color: #64748B; letter-spacing: 1.2px; margin-bottom: 8px;'>TEST VERIFICATION STATUS</p>", unsafe_allow_html=True)
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(f"""
            <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 10px; color: #10B981; font-weight: 700;">PASSED</div>
                <div style="font-size: 18px; font-weight: 800; color: #10B981;">{stats['passed']}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_sb2:
        st.markdown(f"""
            <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 10px; color: #EF4444; font-weight: 700;">FAILED</div>
                <div style="font-size: 18px; font-weight: 800; color: #EF4444;">{stats['failed']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 10px; text-align: center; margin-top: 8px;">
            <div style="font-size: 10px; color: #F59E0B; font-weight: 700;">UNTESTED / PENDING</div>
            <div style="font-size: 18px; font-weight: 800; color: #F59E0B;">{stats['untested']} / {stats['total']}</div>
        </div>
    """, unsafe_allow_html=True)

    # Packet Tracer Integration Architecture Box in Sidebar
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    with st.expander("ℹ️ Packet Tracer Connection Info", expanded=False):
        st.markdown("""
            **Integration Mode: Manual Verification**
            
            - **No Direct Socket**: Cisco Packet Tracer uses a proprietary desktop simulation environment without external Python API bindings by default.
            - **Honest Data Handling**: Configuration and test outcomes are entered or validated manually from real Packet Tracer CLI execution (`show vlan`, `ping`, etc.).
            - **Academic Integrity**: This dashboard does not invent fake real-time telemetry.
        """)

    st.markdown("""
        <div style="margin-top: 30px; padding: 12px; background: rgba(30, 41, 59, 0.4); border-radius: 8px; font-size: 11px; color: #64748B;">
            <b>NetSecure v2.4 (Enterprise Edition)</b><br>
            Designed for Computer Networks College Project & NOC Lab Testing.
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PAGE 1: OVERVIEW & SYSTEM HEALTH
# -----------------------------------------------------------------------------
if selected_page == "📊 1. Overview & Health":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🛡️ NetSecure: Enterprise Network Control Center</h1>
                <p class="noc-subtitle">CENTRALIZED MONITORING & SECURITY VERIFICATION FOR CISCO PACKET TRACER</p>
            </div>
            <div class="noc-badge">● Standalone Companion Mode</div>
        </div>
    """, unsafe_allow_html=True)

    # Required Architecture Disclaimer
    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 18px;">⚠️</span>
            <div>
                <div class="disclaimer-title">Network Simulation Disclaimer & Presentation Scope</div>
                This dashboard is an interactive presentation companion for your Cisco Packet Tracer project topology.
                All IP addressing schemes, VLAN matrices, and test statuses are editable example data.
                This software does not claim a live socket connection to Cisco Packet Tracer. All test outcomes must be verified inside the Packet Tracer CLI.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Project Narrative Overview Card
    st.markdown("""
        <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
            <h3 style="margin: 0 0 10px 0; font-size: 17px; color: #F8FAFC;">Project Architectural Overview</h3>
            <p style="color: #94A3B8; font-size: 13.5px; line-height: 1.6; margin: 0;">
                The <b>NetSecure Enterprise Network</b> implements a robust, segmented campus network architecture designed in <b>Cisco Packet Tracer</b>.
                At the core sits a <b>Cisco Catalyst 3650 Multilayer Switch</b> (<code>Multilayer Switch0</code>) providing high-speed wire-rate Inter-VLAN routing via Switch Virtual Interfaces (SVIs) and centralized Extended Access Control Lists (ACLs).
                The access layer is comprised of three <b>Cisco Catalyst 2960 switches</b> (<code>Switch0</code>, <code>Switch1</code>, and <code>Switch2</code>) servicing three dedicated departments:
                <b>IT & Engineering (Purple Zone)</b>, <b>HR & Administration (Yellow Zone)</b>, and <b>Finance & Accounting (Pink Zone)</b>.
                Each department features dedicated workstations (PCs) and an isolated departmental server.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # KPI Metric Cards Grid
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Departments</div>
                <div class="metric-value">3</div>
                <div class="metric-sub">Purple · Yellow · Pink</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Switches</div>
                <div class="metric-value">4</div>
                <div class="metric-sub">1 Core MLS + 3 Access</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">End-User PCs</div>
                <div class="metric-value">6</div>
                <div class="metric-sub">PC0 to PC5 (2 per Dept)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Servers</div>
                <div class="metric-value">3</div>
                <div class="metric-sub">Server0, 1, 2 (1 per Dept)</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Active VLANs</div>
                <div class="metric-value">3</div>
                <div class="metric-sub">VLANs 10, 20, 30 Configured</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # Two Column Layout: Departmental Zones Summary vs Verification Checklist Summary
    col_left, col_right = st.columns([1.2, 1.0])

    with col_left:
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="font-size: 16px; margin: 0; color: #FFFFFF;">Departmental Segments & Visual Zones</h3>
                <span style="font-size: 11.5px; color: #06B6D4;">Packet Tracer Visual Mapping</span>
            </div>
        """, unsafe_allow_html=True)

        for zone_color, d in data_manager.DEPARTMENTS.items():
            css_class = f"dept-card dept-card-{zone_color.lower()}"
            st.markdown(f"""
                <div class="{css_class}">
                    <div class="dept-title">
                        <span style="color: {d['color_hex']};">{zone_color} Section: {d['name']}</span>
                        <span style="font-size: 11px; color: #94A3B8; background: #0B1120; border: 1px solid #1E293B; padding: 2px 8px; border-radius: 6px;">VLAN {d['vlan_id']}</span>
                    </div>
                    <div style="font-size: 12.5px; color: #CBD5E1; margin: 6px 0;">
                        <b>Switch:</b> <code>{d['switch']}</code> &nbsp;|&nbsp; <b>Workstations:</b> <code>{", ".join(d['pcs'])}</code> &nbsp;|&nbsp; <b>Server:</b> <code>{d['server']}</code>
                    </div>
                    <div style="font-size: 12px; color: #94A3B8;">
                        <b>Subnet:</b> <code>{d['subnet_example']}</code> &nbsp;|&nbsp; <b>Gateway:</b> <code>{d['gateway_example']}</code>
                    </div>
                    <div style="font-size: 11.5px; color: #64748B; margin-top: 6px;">
                        {d['role']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h3 style="font-size: 16px; margin: 0; color: #FFFFFF;">Configuration Checklist KPI</h3>
                <span style="font-size: 11.5px; color: #94A3B8;">Validation Progress</span>
            </div>
        """, unsafe_allow_html=True)

        # Verification Progress Card
        stats = data_manager.get_test_stats()
        st.markdown(f"""
            <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 12px; padding: 18px; margin-bottom: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 13px; font-weight: 700; color: #F8FAFC;">Overall Verification Rate</span>
                    <span style="font-size: 15px; font-weight: 800; color: #06B6D4;">{stats['pass_rate']}%</span>
                </div>
                <div style="background: #1E293B; border-radius: 6px; height: 10px; width: 100%; overflow: hidden; margin-bottom: 16px;">
                    <div style="background: linear-gradient(90deg, #10B981, #06B6D4); width: {stats['pass_rate']}%; height: 100%;"></div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; text-align: center;">
                    <div style="background: #0B1120; border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 8px;">
                        <div style="font-size: 10.5px; color: #10B981; font-weight: 700;">PASSED</div>
                        <div style="font-size: 16px; font-weight: 800; color: #10B981;">{stats['passed']}</div>
                    </div>
                    <div style="background: #0B1120; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 8px;">
                        <div style="font-size: 10.5px; color: #F59E0B; font-weight: 700;">UNTESTED</div>
                        <div style="font-size: 16px; font-weight: 800; color: #F59E0B;">{stats['untested']}</div>
                    </div>
                    <div style="background: #0B1120; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 8px;">
                        <div style="font-size: 10.5px; color: #EF4444; font-weight: 700;">FAILED</div>
                        <div style="font-size: 16px; font-weight: 800; color: #EF4444;">{stats['failed']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Quick Checklist Snapshot
        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px;'>RECENT TEST ITEMS</p>", unsafe_allow_html=True)
        for t in st.session_state.test_checklist[:4]:
            status_cls = "status-passed" if t['status'] == "Passed" else ("status-failed" if t['status'] == "Failed" else "status-untested")
            st.markdown(f"""
                <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div style="font-size: 12.5px; font-weight: 700; color: #F8FAFC;">{t['title']}</div>
                        <div style="font-size: 11px; color: #64748B;"><code>{t['cisco_cmd'].splitlines()[0]}</code></div>
                    </div>
                    <span class="status-pill {status_cls}">{t['status']}</span>
                </div>
            """, unsafe_allow_html=True)

        if st.button("🚀 Open Full Validation Suite", use_container_width=True):
            st.session_state.current_page = "🧪 5. Validation & Test Logs"
            st.rerun()


# -----------------------------------------------------------------------------
# PAGE 2: NETWORK TOPOLOGY
# -----------------------------------------------------------------------------
elif selected_page == "🗺️ 2. Network Topology":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🗺️ Cisco Packet Tracer Network Topology</h1>
                <p class="noc-subtitle">ENTERPRISE 3-TIER DISTRIBUTION & ACCESS LAYER ARCHITECTURAL MODEL</p>
            </div>
            <div class="noc-badge">Logical Topo Model</div>
        </div>
    """, unsafe_allow_html=True)

    # Topology Disclaimer Notice
    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 18px;">ℹ️</span>
            <div>
                <div class="disclaimer-title">Topology Rendering Notice</div>
                The diagram below is dynamically generated to mirror the visible structure and department color zones of your <b>Cisco Packet Tracer</b> design:
                <code>Multilayer Switch0 → Switch0, Switch1, Switch2 → Department PCs & Servers</code>.
                Interface designations (e.g. Gig1/0/1, Fa0/1) represent recommended enterprise port mappings.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Matplotlib Topology Render Container
    with st.spinner("Rendering High-Resolution Topology Diagram..."):
        topo_fig = topology_graph.render_topology_diagram()
        st.pyplot(topo_fig, use_container_width=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # Device Inventory & Link Specifications Table
    st.markdown("### 📋 Complete Device Inventory & Port Mapping")

    inventory_data = [
        {"Device": "Multilayer Switch0", "Role": "Core / Distribution", "Model": "Cisco Catalyst 3650", "Zone": "Core Backbone", "Interfaces": "Gig1/0/1, Gig1/0/2, Gig1/0/3 (Trunk)", "VLANs": "10, 20, 30 (SVIs)", "IP / Gateway": "192.168.10.1, .20.1, .30.1"},
        {"Device": "Switch0", "Role": "Access Switch", "Model": "Cisco Catalyst 2960", "Zone": "Purple (IT Dept)", "Interfaces": "Gig0/1 (Uplink), Fa0/1-10 (Access)", "VLANs": "VLAN 10", "IP / Gateway": "192.168.10.2 (Mgmt)"},
        {"Device": "PC0", "Role": "Engineering Workstation", "Model": "Generic PC", "Zone": "Purple (IT Dept)", "Interfaces": "FastEthernet 0/1", "VLANs": "VLAN 10", "IP / Gateway": "192.168.10.11 / GW: .10.1"},
        {"Device": "PC1", "Role": "DevOps Workstation", "Model": "Generic PC", "Zone": "Purple (IT Dept)", "Interfaces": "FastEthernet 0/2", "VLANs": "VLAN 10", "IP / Gateway": "192.168.10.12 / GW: .10.1"},
        {"Device": "Server0", "Role": "Infrastructure DNS/Web", "Model": "Generic Server", "Zone": "Purple (IT Dept)", "Interfaces": "FastEthernet 0/10", "VLANs": "VLAN 10", "IP / Gateway": "192.168.10.100 / GW: .10.1"},
        {"Device": "Switch1", "Role": "Access Switch", "Model": "Cisco Catalyst 2960", "Zone": "Yellow (HR Dept)", "Interfaces": "Gig0/1 (Uplink), Fa0/1-10 (Access)", "VLANs": "VLAN 20", "IP / Gateway": "192.168.20.2 (Mgmt)"},
        {"Device": "PC2", "Role": "Recruitment Workstation", "Model": "Generic PC", "Zone": "Yellow (HR Dept)", "Interfaces": "FastEthernet 0/1", "VLANs": "VLAN 20", "IP / Gateway": "192.168.20.11 / GW: .20.1"},
        {"Device": "PC3", "Role": "HR Generalist Workstation", "Model": "Generic PC", "Zone": "Yellow (HR Dept)", "Interfaces": "FastEthernet 0/2", "VLANs": "VLAN 20", "IP / Gateway": "192.168.20.12 / GW: .20.1"},
        {"Device": "Server1", "Role": "HR Portal & Records", "Model": "Generic Server", "Zone": "Yellow (HR Dept)", "Interfaces": "FastEthernet 0/10", "VLANs": "VLAN 20", "IP / Gateway": "192.168.20.100 / GW: .20.1"},
        {"Device": "Switch2", "Role": "Access Switch", "Model": "Cisco Catalyst 2960", "Zone": "Pink (Finance Dept)", "Interfaces": "Gig0/1 (Uplink), Fa0/1-10 (Access)", "VLANs": "VLAN 30", "IP / Gateway": "192.168.30.2 (Mgmt)"},
        {"Device": "PC4", "Role": "Billing & Audit PC", "Model": "Generic PC", "Zone": "Pink (Finance Dept)", "Interfaces": "FastEthernet 0/1", "VLANs": "VLAN 30", "IP / Gateway": "192.168.30.11 / GW: .30.1"},
        {"Device": "PC5", "Role": "Payroll Accounts PC", "Model": "Generic PC", "Zone": "Pink (Finance Dept)", "Interfaces": "FastEthernet 0/2", "VLANs": "VLAN 30", "IP / Gateway": "192.168.30.12 / GW: .30.1"},
        {"Device": "Server2", "Role": "Financial Accounting DB", "Model": "Generic Server", "Zone": "Pink (Finance Dept)", "Interfaces": "FastEthernet 0/10", "VLANs": "VLAN 30", "IP / Gateway": "192.168.30.100 / GW: .30.1"}
    ]

    inv_df = pd.DataFrame(inventory_data)
    st.dataframe(inv_df, use_container_width=True, hide_index=True)

    csv_inv = data_manager.convert_df_to_csv(inv_df)
    st.download_button(
        label="📥 Export Device Inventory to CSV",
        data=csv_inv,
        file_name="NetSecure_Device_Inventory.csv",
        mime="text/csv"
    )


# -----------------------------------------------------------------------------
# PAGE 3: VLAN AND IP ADDRESSING
# -----------------------------------------------------------------------------
elif selected_page == "🌐 3. VLAN & IP Addressing":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🌐 VLAN Segmentation & IP Addressing Plan</h1>
                <p class="noc-subtitle">INTERACTIVE SUBNET MATRIX, EDITABLE GATEWAYS, AND ENDPOINT DIRECTORY</p>
            </div>
            <div class="noc-badge">Editable Configuration</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 18px;">✏️</span>
            <div>
                <div class="disclaimer-title">Editable Example Data Notice</div>
                The IP addresses, subnet masks, and default gateways below are structured example defaults based on your Packet Tracer topology.
                You can directly edit the values in the tables below to reflect your specific college assignment configuration, then export the result to CSV.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Section 1: Departmental VLANs Table
    st.markdown("### 🏢 Departmental VLAN Configuration")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Double-click any cell below to modify Network Address, Subnet Mask, Gateway, or Assigned Devices.</p>", unsafe_allow_html=True)

    edited_vlans = st.data_editor(
        st.session_state.vlans_df,
        use_container_width=True,
        num_rows="dynamic",
        key="vlan_editor"
    )
    # Update session state with edits
    st.session_state.vlans_df = edited_vlans

    col_vlan_down, col_vlan_reset = st.columns([1, 4])
    with col_vlan_down:
        csv_vlans = data_manager.convert_df_to_csv(st.session_state.vlans_df)
        st.download_button(
            label="📥 Download VLAN Plan CSV",
            data=csv_vlans,
            file_name="NetSecure_VLAN_Plan.csv",
            mime="text/csv"
        )
    with col_vlan_reset:
        if st.button("🔄 Reset VLAN Plan to Defaults"):
            st.session_state.vlans_df = data_manager.get_initial_vlans_df()
            st.rerun()

    st.markdown("---")

    # Section 2: Endpoint IP Allocation Matrix
    st.markdown("### 🖥️ Endpoint IP Allocation Matrix (Workstations & Servers)")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Detailed device-level IP mapping matching PC0-PC5 and Server0-Server2 in Cisco Packet Tracer.</p>", unsafe_allow_html=True)

    edited_endpoints = st.data_editor(
        st.session_state.endpoints_df,
        use_container_width=True,
        num_rows="dynamic",
        key="endpoints_editor"
    )
    st.session_state.endpoints_df = edited_endpoints

    col_ep_down, col_ep_reset = st.columns([1, 4])
    with col_ep_down:
        csv_endpoints = data_manager.convert_df_to_csv(st.session_state.endpoints_df)
        st.download_button(
            label="📥 Download Endpoints CSV",
            data=csv_endpoints,
            file_name="NetSecure_Endpoint_Allocation.csv",
            mime="text/csv"
        )
    with col_ep_reset:
        if st.button("🔄 Reset Endpoints to Defaults"):
            st.session_state.endpoints_df = data_manager.get_initial_endpoints_df()
            st.rerun()

    st.markdown("---")

    # Section 3: Subnet Calculator Helper for College Project
    st.markdown("### 🧮 Subnet Address Range Calculator")
    calc_c1, calc_c2, calc_c3 = st.columns(3)
    with calc_c1:
        calc_vlan = st.selectbox("Select Target VLAN", ["VLAN 10 (IT)", "VLAN 20 (HR)", "VLAN 30 (Finance)"])
    with calc_c2:
        subnet_input = st.text_input("Network Address (CIDR)", value="192.168.10.0/24" if "10" in calc_vlan else ("192.168.20.0/24" if "20" in calc_vlan else "192.168.30.0/24"))
    with calc_c3:
        gw_input = st.text_input("Assigned Default Gateway (MLS SVI)", value="192.168.10.1" if "10" in calc_vlan else ("192.168.20.1" if "20" in calc_vlan else "192.168.30.1"))

    st.markdown(f"""
        <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 14px; margin-top: 10px;">
            <div style="font-size: 13px; font-weight: 700; color: #38BDF8; margin-bottom: 6px;">Subnet Technical Specs for {calc_vlan}:</div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 12px; color: #CBD5E1;">
                <div><b>Network Base:</b> <code>{subnet_input.split('/')[0]}</code></div>
                <div><b>Broadcast IP:</b> <code>{subnet_input.split('.')[0]}.{subnet_input.split('.')[1]}.{subnet_input.split('.')[2]}.255</code></div>
                <div><b>Usable Host Range:</b> <code>.2 — .254</code></div>
                <div><b>Gateway (SVI):</b> <code>{gw_input}</code></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PAGE 4: SECURITY POLICY & ACL PLANNER
# -----------------------------------------------------------------------------
elif selected_page == "🔒 4. Security Policy & ACL":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🔒 Enterprise Security Policies & Access Control Lists</h1>
                <p class="noc-subtitle">DEPARTMENTAL TRAFFIC ISOLATION & CISCO IOS EXTENDED ACL COMPILER</p>
            </div>
            <div class="noc-badge">Access Control Engine</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 18px;">🛡️</span>
            <div>
                <div class="disclaimer-title">Security Policy Distinction Notice</div>
                The rules listed here represent <b>proposed and planned security policies</b>.
                They must not be confused with ACLs that have already been tested and confirmed on the physical or simulated switches.
                Use the compiler below to generate Cisco IOS commands, apply them on <code>Multilayer Switch0</code>, and verify them under the Validation page.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Section 1: Security Policies Table
    st.markdown("### 📜 Security Access Control Matrix")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Specify traffic direction, permit/deny actions, target protocols, and verification status.</p>", unsafe_allow_html=True)

    edited_sec = st.data_editor(
        st.session_state.security_policies_df,
        use_container_width=True,
        num_rows="dynamic",
        key="security_policies_editor"
    )
    st.session_state.security_policies_df = edited_sec

    col_sec_down, col_sec_reset = st.columns([1, 4])
    with col_sec_down:
        csv_sec = data_manager.convert_df_to_csv(st.session_state.security_policies_df)
        st.download_button(
            label="📥 Download Security Policies CSV",
            data=csv_sec,
            file_name="NetSecure_Security_Policies.csv",
            mime="text/csv"
        )
    with col_sec_reset:
        if st.button("🔄 Reset Policies to Defaults"):
            st.session_state.security_policies_df = data_manager.get_initial_security_policies_df()
            st.rerun()

    st.markdown("---")

    # Section 2: Cisco IOS Extended ACL Script Generator
    st.markdown("### ⚙️ Cisco IOS Extended ACL Generator (Catalyst 3650)")
    st.markdown("""
        <p style="font-size: 12.5px; color: #94A3B8;">
            This compiler converts your defined security matrix into verified Cisco IOS Extended Access Control Lists.
            Copy and paste this script directly into the CLI of <code>Multilayer Switch0</code>.
        </p>
    """, unsafe_allow_html=True)

    acl_script = cisco_helpers.generate_cisco_acl_script(
        st.session_state.security_policies_df,
        st.session_state.vlans_df
    )

    st.code(acl_script, language="cisco")

    st.download_button(
        label="💾 Download Cisco IOS ACL Script (.txt)",
        data=acl_script,
        file_name="NetSecure_Cisco_ACL_Config.txt",
        mime="text/plain"
    )


# -----------------------------------------------------------------------------
# PAGE 5: VALIDATION AND TEST LOGS
# -----------------------------------------------------------------------------
elif selected_page == "🧪 5. Validation & Test Logs":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🧪 Network Validation Suite & Test Logs</h1>
                <p class="noc-subtitle">VERIFICATION CHECKLIST, CISCO CLI REFERENCE, AND EVIDENCE LOGS</p>
            </div>
            <div class="noc-badge">Zero Auto-Pass Enforcement</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 18px;">🔬</span>
            <div>
                <div class="disclaimer-title">Strict Manual Verification Policy</div>
                In accordance with academic testing protocols, <b>no test is ever marked as 'Passed' automatically</b>.
                You must execute each Cisco command or ping inside Cisco Packet Tracer, observe the terminal response, and record the verified outcome below.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Verification Progress Metric Cards
    stats = data_manager.get_test_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Tests Defined</div>
                <div class="metric-value">{stats['total']}</div>
                <div class="metric-sub">Across 8 Categories</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #10B981;">
                <div class="metric-label" style="color: #10B981;">Verified Passed</div>
                <div class="metric-value" style="color: #10B981;">{stats['passed']}</div>
                <div class="metric-sub">Confirmed in Packet Tracer</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #F59E0B;">
                <div class="metric-label" style="color: #F59E0B;">Not Tested / Pending</div>
                <div class="metric-value" style="color: #F59E0B;">{stats['untested']}</div>
                <div class="metric-sub">Awaiting CLI Execution</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #EF4444;">
                <div class="metric-label" style="color: #EF4444;">Failed / Blocked</div>
                <div class="metric-value" style="color: #EF4444;">{stats['failed']}</div>
                <div class="metric-sub">Requiring Troubleshooting</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # Tabs: Interactive Checklist vs Cisco CLI Output Inspector vs Cisco Commands Guide
    tab_tests, tab_inspector, tab_cli_ref = st.tabs([
        "📋 Interactive Test Checklist & Recorder",
        "🔍 Cisco CLI Output Inspector",
        "📖 Cisco Catalyst CLI Reference Guide"
    ])

    # TAB 1: Interactive Checklist
    with tab_tests:
        st.markdown("### 📝 Record Verification Test Results")
        st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Update the status of each test item below after executing the corresponding command in Cisco Packet Tracer.</p>", unsafe_allow_html=True)

        for i, test in enumerate(st.session_state.test_checklist):
            status_color = "#10B981" if test["status"] == "Passed" else ("#EF4444" if test["status"] == "Failed" else "#F59E0B")
            
            with st.expander(f"**[{test['id']}] {test['title']}** — Status: **{test['status']}** ({test['category']})", expanded=(test["status"] == "Not Tested")):
                st.markdown(f"""
                    <div style="font-size: 13px; color: #E2E8F0; margin-bottom: 8px;">
                        <b>Objective:</b> {test['description']}
                    </div>
                """, unsafe_allow_html=True)

                col_t1, col_t2 = st.columns([1.2, 1.0])
                with col_t1:
                    st.markdown("**Cisco Verification Command:**")
                    st.code(test['cisco_cmd'], language="cisco")
                    st.markdown(f"**Expected Outcome:** `{test['expected_outcome']}`")
                
                with col_t2:
                    st.markdown("**Record Test Result:**")
                    new_status = st.selectbox(
                        "Outcome",
                        ["Not Tested", "Passed", "Failed"],
                        index=["Not Tested", "Passed", "Failed"].index(test["status"]),
                        key=f"status_select_{test['id']}"
                    )

                    new_notes = st.text_input(
                        "Verification Notes / Terminal Output Snippet",
                        value=test.get("notes", ""),
                        key=f"notes_input_{test['id']}"
                    )

                    if st.button("💾 Save Test Result", key=f"btn_save_{test['id']}"):
                        st.session_state.test_checklist[i]["status"] = new_status
                        st.session_state.test_checklist[i]["notes"] = new_notes
                        st.session_state.test_checklist[i]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success(f"Updated {test['id']} result to {new_status}!")
                        st.rerun()

                st.markdown(f"<div style='font-size: 11px; color: #64748B; margin-top: 6px;'>Last Updated: {test.get('timestamp', 'Never')}</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Test Log Table & Export
        st.markdown("### 📊 Test Logs Summary Table")
        test_df = pd.DataFrame(st.session_state.test_checklist)[["id", "category", "title", "cisco_cmd", "status", "timestamp", "notes"]]
        st.dataframe(test_df, use_container_width=True, hide_index=True)

        col_log_down, col_log_reset = st.columns([1, 4])
        with col_log_down:
            csv_logs = data_manager.convert_df_to_csv(test_df)
            st.download_button(
                label="📥 Export Full Test Logs CSV",
                data=csv_logs,
                file_name="NetSecure_Validation_Logs.csv",
                mime="text/csv"
            )
        with col_log_reset:
            if st.button("⚠️ Reset All Tests to 'Not Tested'"):
                st.session_state.test_checklist = data_manager.get_initial_test_checklist()
                st.success("All test logs have been reset.")
                st.rerun()

    # TAB 2: Cisco CLI Output Inspector
    with tab_inspector:
        st.markdown("### 🔍 Live CLI Output Analyzer")
        st.markdown("""
            <p style="font-size: 12.5px; color: #94A3B8;">
                Paste actual terminal output copied from Cisco Packet Tracer below (or load a sample output) to automatically inspect for key verification flags.
            </p>
        """, unsafe_allow_html=True)

        sample_choice = st.selectbox(
            "Load Sample Cisco CLI Output",
            ["-- Select or Paste Custom Output --"] + list(cisco_helpers.SAMPLE_CLI_OUTPUTS.keys())
        )

        default_text = ""
        if sample_choice in cisco_helpers.SAMPLE_CLI_OUTPUTS:
            default_text = cisco_helpers.SAMPLE_CLI_OUTPUTS[sample_choice]

        user_cli_text = st.text_area(
            "Cisco CLI Output Text",
            value=default_text,
            height=200,
            placeholder="Paste output from: show vlan brief, show interfaces trunk, show ip interface brief, ping..."
        )

        if st.button("🔎 Analyze CLI Output"):
            analysis = cisco_helpers.parse_cisco_output(user_cli_text)
            
            badge_color = "#10B981" if analysis["status"] == "Success" else ("#EF4444" if analysis["status"] == "Alert" else "#F59E0B")
            
            st.markdown(f"""
                <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 16px; margin-top: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 700; color: #FFFFFF;">Command Detected: <code>{analysis['detected_type']}</code></span>
                        <span style="background: {badge_color}22; color: {badge_color}; border: 1px solid {badge_color}; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700;">
                            {analysis['status'].upper()}
                        </span>
                    </div>
                    <div style="font-size: 13px; color: #E2E8F0; margin-bottom: 10px;">
                        <b>Summary:</b> {analysis['summary']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if analysis["details"]:
                st.markdown("<p style='font-size: 12px; font-weight: 700; color: #94A3B8; margin-top: 10px;'>MATCHED VERIFICATION ENTRIES:</p>", unsafe_allow_html=True)
                for item in analysis["details"]:
                    st.markdown(f"- `{item}`")

    # TAB 3: Cisco Commands Reference Guide
    with tab_cli_ref:
        st.markdown("### 📖 Cisco Catalyst Configuration & Verification Cheatsheet")
        st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Essential commands used for configuring and verifying the NetSecure architecture in Cisco Packet Tracer.</p>", unsafe_allow_html=True)

        for topic, content in cisco_helpers.CISCO_CLI_REFERENCES.items():
            with st.expander(f"📌 {topic} ({content['device']})"):
                st.markdown(f"**Target Device:** `{content['device']}`")
                st.markdown("**Configuration Commands:**")
                st.code(content['commands'], language="cisco")
                st.markdown(f"**Verification CLI Command:** `{content['verification']}`")

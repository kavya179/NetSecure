"""
NetSecure: Enterprise Network Design & Security Dashboard
Cisco Packet Tracer Companion & Network Operations Center (NOC) Dashboard
Built with Python, Streamlit, Pandas, and Matplotlib.
Accurately mirrors verified Cisco Packet Tracer network facts without fabricated live telemetry.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import ipaddress

# Import custom modular helpers
import importlib
import data_manager
import topology_graph
import cisco_helpers

# Dynamic module reload to ensure newest helper code is active
importlib.reload(data_manager)
importlib.reload(topology_graph)
importlib.reload(cisco_helpers)

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
        margin-bottom: 20px;
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
        font-size: 12.5px;
        color: var(--cyan-accent);
        margin: 4px 0 0 0;
        font-weight: 600;
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
        font-size: 11.5px;
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
        background: rgba(15, 23, 42, 0.85);
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
        gap: 12px;
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
        font-size: 10.5px;
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
# SIDEBAR NAVIGATION & NOC STATUS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="padding: 10px 0 16px 0; border-bottom: 1px solid #1E293B;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="background: linear-gradient(135deg, #06B6D4, #3B82F6); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 900; color: #0B1120;">
                    🛡️
                </div>
                <div>
                    <div style="font-size: 17px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px;">NetSecure</div>
                    <div style="font-size: 10px; color: #06B6D4; letter-spacing: 0.8px; font-weight: 700;">NOC DASHBOARD</div>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 11.5px; color: #94A3B8; line-height: 1.4;">
                Cisco Packet Tracer Companion & Verification Center
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='font-size: 10.5px; font-weight: 700; color: #64748B; letter-spacing: 1.2px; margin: 16px 0 6px 4px;'>PAGES</p>", unsafe_allow_html=True)
    
    pages = [
        "📊 1. Overview & Verified Inventory",
        "🗺️ 2. Network Topology",
        "🌐 3. VLAN & IP Addressing",
        "🔒 4. Security Policy & ACL Generator",
        "🧪 5. Validation & Test Logs"
    ]
    
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

    # Verification Health Metrics (PASS / FAIL / NOT TESTED)
    stats = data_manager.get_test_stats()
    st.markdown("<p style='font-size: 10.5px; font-weight: 700; color: #64748B; letter-spacing: 1.2px; margin-bottom: 8px;'>TEST VERIFICATION AUDIT</p>", unsafe_allow_html=True)
    
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.markdown(f"""
            <div style="background: #111A2E; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 10px; color: #10B981; font-weight: 700;">VERIFIED PASS</div>
                <div style="font-size: 20px; font-weight: 800; color: #10B981;">{stats['passed']}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_sb2:
        st.markdown(f"""
            <div style="background: #111A2E; border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 8px; padding: 10px; text-align: center;">
                <div style="font-size: 10px; color: #EF4444; font-weight: 700;">FAIL</div>
                <div style="font-size: 20px; font-weight: 800; color: #EF4444;">{stats['failed']}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background: #111A2E; border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 8px; padding: 10px; text-align: center; margin-top: 8px;">
            <div style="font-size: 10px; color: #F59E0B; font-weight: 700;">NOT TESTED / PENDING</div>
            <div style="font-size: 20px; font-weight: 800; color: #F59E0B;">{stats['untested']} / {stats['total']}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin-top: 24px; padding: 12px; background: rgba(30, 41, 59, 0.5); border-left: 3px solid #06B6D4; border-radius: 6px; font-size: 11px; color: #94A3B8; line-height: 1.4;">
            <b>Integration Notice:</b><br>
            Packet Tracer simulation is not connected directly. Results are recorded manually from real CLI outputs.
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# GLOBAL SIMULATION NOTICE ON EVERY PAGE
# -----------------------------------------------------------------------------
st.markdown("""
    <div class="disclaimer-banner">
        <span style="font-size: 20px;">⚠️</span>
        <div>
            <div class="disclaimer-title">Cisco Packet Tracer Integration Notice</div>
            Packet Tracer simulation is not connected directly. Results are recorded manually from real CLI outputs.
            This dashboard does not invent live device statuses, fake socket streams, or fabricated test passes.
        </div>
    </div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PAGE 1: OVERVIEW & SYSTEM HEALTH
# -----------------------------------------------------------------------------
if selected_page == "📊 1. Overview & Verified Inventory":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🛡️ NetSecure: Network Operations Center</h1>
                <p class="noc-subtitle">ENTERPRISE NETWORK DESIGN & SECURITY COMPANION FOR CISCO PACKET TRACER</p>
            </div>
            <div class="noc-badge">Companion Mode</div>
        </div>
    """, unsafe_allow_html=True)

    # Narrative Overview
    st.markdown("""
        <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 12px; padding: 18px 22px; margin-bottom: 22px;">
            <h3 style="margin: 0 0 8px 0; font-size: 16.5px; color: #F8FAFC;">Verified Network Architecture</h3>
            <p style="color: #94A3B8; font-size: 13px; line-height: 1.6; margin: 0;">
                The <b>NetSecure Enterprise Network</b> is built in <b>Cisco Packet Tracer</b> using a hierarchical distribution and access model:
                One central <b>Cisco 3650 Multilayer Switch</b> (<code>Multilayer Switch0</code>) connecting to three access switches:
                <code>Switch0</code>, <code>Switch1</code>, and <code>Switch2</code>.
                The network organizes endpoints into three visual department zones corresponding to verified VLANs:
                <b>Management (VLAN 10)</b> in the Purple Zone, <b>finance (VLAN 20)</b> in the Yellow Zone, and <b>IT (VLAN 30)</b> in the Pink Zone.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Metric Cards Grid
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
                <div class="metric-sub">1 Core MLS0 + 3 Access</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-label">Workstations</div>
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
                <div class="metric-label">Verified VLANs</div>
                <div class="metric-value">3</div>
                <div class="metric-sub">10 (Mgmt), 20 (fin), 30 (IT)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 22px;'></div>", unsafe_allow_html=True)

    # Two Column Layout: Departmental Zones vs Verified vs Unverified Facts
    col_left, col_right = st.columns([1.15, 1.0])

    with col_left:
        st.markdown("### 🏢 Department Segments & Verified VLANs")

        for zone_color, d in data_manager.DEPARTMENTS.items():
            css_class = f"dept-card dept-card-{zone_color.lower()}"
            verified_list = d.get("verified_devices", [])
            verified_str = ", ".join(verified_list) if verified_list else "None yet confirmed"
            unverified_list = d.get("unverified_devices", [])
            unverified_str = ", ".join(unverified_list) if unverified_list else "None"
            st.markdown(f"""
                <div class="{css_class}">
                    <div class="dept-title">
                        <span style="color: {d['color_hex']};">{zone_color} Section: {d['name']}</span>
                        <span style="font-size: 11px; color: #94A3B8; background: #0B1120; border: 1px solid #1E293B; padding: 2px 8px; border-radius: 6px;">VLAN {d['vlan_id']}</span>
                    </div>
                    <div style="font-size: 12px; color: #CBD5E1; margin: 6px 0;">
                        <b>Assigned Switch:</b> <code>{d['switch']}</code> &nbsp;|&nbsp; <b>Subnet:</b> <code>{d['subnet']}</code> &nbsp;|&nbsp; <b>Gateway:</b> <code>{d['gateway']}</code>
                    </div>
                    <div style="font-size: 11.5px; color: #10B981; margin-top: 4px;">
                        <b>Verified Devices:</b> {verified_str}
                    </div>
                    <div style="font-size: 11.5px; color: #F59E0B; margin-top: 2px;">
                        <b>Unverified Devices:</b> {unverified_str}
                    </div>
                    <div style="font-size: 11px; color: #64748B; margin-top: 6px;">
                        {d['role']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### 📋 Evidence Audit: Verified vs. Unverified")

        st.markdown("""
            <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 12px; padding: 16px; margin-bottom: 14px;">
                <div style="font-size: 13px; font-weight: 700; color: #10B981; margin-bottom: 8px;">
                    ✅ CONFIRMED FACTS (From Packet Tracer Screenshots):
                </div>
                <ul style="font-size: 12px; color: #CBD5E1; margin: 0; padding-left: 18px; line-height: 1.6;">
                    <li><b>VLANs:</b> VLAN 10 (Management), VLAN 20 (finance), VLAN 30 (IT).</li>
                    <li><b>Sample Switch Ports:</b> Fa0/1 -> VLAN 10, Fa0/2 -> VLAN 20, Fa0/3 -> VLAN 30 (Observed on sample access switch CLI output; exact port mapping across all switches is unverified).</li>
                    <li><b>Sample Switch Trunk:</b> Gig0/1 trunking, 802.1Q, native VLAN 1, VLANs 10, 20, 30 allowed.</li>
                    <li><b>DHCP Pools:</b> Management (10.0/24, GW 10.1), finance (20.0/24, GW 20.1, DNS 8.8.8.8), IT (30.0/24, GW 30.1, DNS 8.8.8.8). Excluded: .1 on all.</li>
                    <li><b>PC0 Verified:</b> IP 192.168.10.3, Mask 255.255.255.0, Gateway 192.168.10.1.</li>
                    <li><b>PC2 Verified:</b> IP 192.168.20.3 (Verified via ipconfig screenshot).</li>
                    <li><b>Confirmed Ping 1:</b> PC0 -> 192.168.10.1 (PASS, 4/4 received, 0% loss, Default Gateway).</li>
                    <li><b>Confirmed Ping 2:</b> PC0 -> 192.168.20.3 (PASS, 4/4 received, 0% loss, Cross-Subnet Reachability).</li>
                </ul>
            </div>

            <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 12px; padding: 16px;">
                <div style="font-size: 13px; font-weight: 700; color: #F59E0B; margin-bottom: 8px;">
                    ⏳ UNVERIFIED ITEMS (Pending Direct CLI Confirmation):
                </div>
                <ul style="font-size: 12px; color: #94A3B8; margin: 0; padding-left: 18px; line-height: 1.6;">
                    <li>Multilayer Switch0 routing table (<code>show ip route</code>).</li>
                    <li>All other PC & server IPs (PC1, PC3, PC4, PC5, Server0, Server1, Server2) and switch management IPs.</li>
                    <li>Exact port assignments on Switch0, Switch1, and Switch2 (treated as illustrative examples).</li>
                    <li>Server reachability and services (HTTP/DNS/SQL).</li>
                    <li>ACL enforcement & restriction behavior in Packet Tracer (illustrative templates only).</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)


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

    st.markdown("""
        <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 10px; padding: 12px 16px; margin-bottom: 16px; font-size: 12.5px; color: #94A3B8;">
            <b>Topology Notice:</b> The diagram below illustrates the actual layout of your Cisco Packet Tracer project:
            <code>Multilayer Switch0 → Switch0, Switch1, Switch2 → Department PCs & Servers</code>.
            Verified links and devices (such as Gig0/1 trunk and PC0: 192.168.10.3, PC2: 192.168.20.3) are prominently highlighted in <b>Green</b>.
            Connections whose exact switch ports are not yet confirmed in CLI are depicted as illustrative models with dotted links.
        </div>
    """, unsafe_allow_html=True)

    # Matplotlib Topology Render Container
    with st.spinner("Rendering High-Resolution Topology Diagram..."):
        topo_fig = topology_graph.render_topology_diagram()
        st.pyplot(topo_fig, use_container_width=True)

    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    # Detailed Device Inventory & Interface Mapping Table
    st.markdown("### 📋 Complete Device Inventory & Port Mapping")

    inventory_data = [
        {"Device": "Multilayer Switch0", "Role": "Core / Distribution", "Model": "Cisco Catalyst 3650", "Zone": "Core Backbone", "Interfaces": "Trunk uplinks to Switch0, Switch1, Switch2 (Example port mapping)", "VLANs": "10, 20, 30 (SVIs)", "Verified_IP": "Gateways: 192.168.10.1, 192.168.20.1, 192.168.30.1", "Status": "VERIFIED MODEL"},
        {"Device": "Switch0", "Role": "Access Switch", "Model": "Cisco Catalyst 2960", "Zone": "Purple (Management)", "Interfaces": "Gig0/1 (Verified Trunk), Fa0/1 (Example/unverified port mapping)", "VLANs": "VLAN 10", "Verified_IP": "Unverified / Not configured", "Status": "VERIFIED"},
        {"Device": "PC0", "Role": "Workstation", "Model": "Generic PC", "Zone": "Purple (Management)", "Interfaces": "FastEthernet0 (Port mapping to Switch0 Fa0/1 is example/unverified)", "VLANs": "VLAN 10", "Verified_IP": "192.168.10.3", "Status": "VERIFIED (ipconfig)"},
        {"Device": "PC1", "Role": "Workstation", "Model": "Generic PC", "Zone": "Purple (Management)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 10", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"},
        {"Device": "Server0", "Role": "Management Server", "Model": "Generic Server", "Zone": "Purple (Management)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 10", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"},
        {"Device": "Switch1", "Role": "Access Switch", "Model": "Cisco Catalyst 2960", "Zone": "Yellow (finance)", "Interfaces": "Uplink trunk, Fa0/2 (Example/unverified port mapping)", "VLANs": "VLAN 20", "Verified_IP": "Unverified / Not configured", "Status": "VERIFIED MODEL"},
        {"Device": "PC2", "Role": "Workstation", "Model": "Generic PC", "Zone": "Yellow (finance)", "Interfaces": "FastEthernet0 (Port mapping to Switch1 Fa0/2 is example/unverified)", "VLANs": "VLAN 20", "Verified_IP": "192.168.20.3", "Status": "VERIFIED (ipconfig)"},
        {"Device": "PC3", "Role": "Workstation", "Model": "Generic PC", "Zone": "Yellow (finance)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 20", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"},
        {"Device": "Server1", "Role": "Finance Server", "Model": "Generic Server", "Zone": "Yellow (finance)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 20", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"},
        {"Device": "Switch2", "Role": "Access Switch", "Model": "Cisco Catalyst 2960", "Zone": "Pink (IT)", "Interfaces": "Uplink trunk, Fa0/3 (Example/unverified port mapping)", "VLANs": "VLAN 30", "Verified_IP": "Unverified / Not configured", "Status": "VERIFIED MODEL"},
        {"Device": "PC4", "Role": "Workstation", "Model": "Generic PC", "Zone": "Pink (IT)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 30", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"},
        {"Device": "PC5", "Role": "Workstation", "Model": "Generic PC", "Zone": "Pink (IT)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 30", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"},
        {"Device": "Server2", "Role": "IT Server", "Model": "Generic Server", "Zone": "Pink (IT)", "Interfaces": "FastEthernet0 (Port unverified / example)", "VLANs": "VLAN 30", "Verified_IP": "Unverified / Example only", "Status": "UNVERIFIED"}
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
                <p class="noc-subtitle">VERIFIED SUBNET CONFIGURATIONS, ENDPOINT DIRECTORY, AND ARBITRARY CIDR CALCULATOR</p>
            </div>
            <div class="noc-badge">Editable Configuration</div>
        </div>
    """, unsafe_allow_html=True)

    # Section 1: Departmental VLANs Table
    st.markdown("### 🏢 Departmental VLAN Configuration")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Verified from Packet Tracer switch output: VLAN 10 = Management, VLAN 20 = finance, VLAN 30 = IT.</p>", unsafe_allow_html=True)

    edited_vlans = st.data_editor(
        st.session_state.vlans_df,
        use_container_width=True,
        num_rows="dynamic",
        key="vlan_editor"
    )
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
    st.markdown("### 🖥️ Endpoint Device Directory (Workstations & Servers)")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Explicitly flags verified endpoints (PC0: 192.168.10.3, PC2: 192.168.20.3) vs unverified endpoints.</p>", unsafe_allow_html=True)

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

    # Section 3: Subnet Calculator Powered by Standard ipaddress Module
    st.markdown("### 🧮 Arbitrary IPv4 Subnet Calculator (Standard Library `ipaddress`)")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Calculates network address, broadcast address, netmask, wildcard mask, and usable host range for any CIDR (/0 to /32).</p>", unsafe_allow_html=True)

    calc_c1, calc_c2 = st.columns([1.2, 2.0])
    with calc_c1:
        preset_choice = st.selectbox(
            "Select Verified Preset or Custom",
            [
                "VLAN 10 (Management): 192.168.10.0/24",
                "VLAN 20 (finance): 192.168.20.0/24",
                "VLAN 30 (IT): 192.168.30.0/24",
                "Custom Subnet (/26 Subnet Example): 10.0.0.0/26",
                "Custom Point-to-Point (/30 Example): 172.16.1.0/30",
                "Custom Input..."
            ]
        )
        if "192.168.10.0" in preset_choice:
            default_calc_ip = "192.168.10.0/24"
        elif "192.168.20.0" in preset_choice:
            default_calc_ip = "192.168.20.0/24"
        elif "192.168.30.0" in preset_choice:
            default_calc_ip = "192.168.30.0/24"
        elif "10.0.0.0/26" in preset_choice:
            default_calc_ip = "10.0.0.0/26"
        elif "172.16.1.0/30" in preset_choice:
            default_calc_ip = "172.16.1.0/30"
        else:
            default_calc_ip = "192.168.10.0/24"

        user_cidr = st.text_input("Enter IPv4 Network Address with CIDR", value=default_calc_ip)

    with calc_c2:
        subnet_input = user_cidr.strip() if user_cidr else ""
        if not subnet_input:
            st.warning("Please enter an IPv4 network CIDR (e.g. 192.168.10.0/24, 10.0.0.0/26, 172.16.1.0/30).")
        else:
            try:
                # Direct calculation using Python's standard ipaddress module with strict=False
                raw_cidr = subnet_input if "/" in subnet_input else f"{subnet_input}/24"
                net = ipaddress.ip_network(raw_cidr, strict=False)

                # Calculate network properties
                network_address = str(net.network_address)
                netmask = str(net.netmask)
                wildcard_mask = str(net.hostmask)
                prefixlen = net.prefixlen
                total_addresses = net.num_addresses
                address_scope = "Private (RFC 1918)" if net.is_private else "Public Internet"

                # Calculate broadcast and usable host range
                if net.prefixlen <= 30:
                    broadcast_address = str(net.broadcast_address)
                    usable_hosts = max(0, net.num_addresses - 2)
                    first_host = str(net.network_address + 1)
                    last_host = str(net.broadcast_address - 1)
                    usable_range = f"{first_host} - {last_host}"
                elif net.prefixlen == 31:
                    broadcast_address = "N/A (RFC 3021 Point-to-Point)"
                    usable_hosts = 2
                    usable_range = f"{net.network_address} - {net.broadcast_address} (RFC 3021 Point-to-Point)"
                else:  # /32
                    broadcast_address = "N/A (Single Host IP)"
                    usable_hosts = 1
                    usable_range = f"{net.network_address} (Single Host)"

                st.markdown(f"""
                    <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 10px; padding: 14px;">
                        <div style="font-size: 13.5px; font-weight: 700; color: #38BDF8; margin-bottom: 8px;">
                            Subnet Calculation Results for <code>{subnet_input}</code>:
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-size: 12px; color: #CBD5E1;">
                            <div><b>Network Address:</b> <code>{network_address}</code></div>
                            <div><b>Broadcast Address:</b> <code>{broadcast_address}</code></div>
                            <div><b>Subnet Netmask:</b> <code>{netmask}</code></div>
                            <div><b>Wildcard Mask:</b> <code>{wildcard_mask}</code></div>
                            <div><b>Usable Host Range:</b> <code>{usable_range}</code></div>
                            <div><b>Usable Hosts:</b> <code>{usable_hosts}</code> / {total_addresses} total</div>
                            <div><b>CIDR Prefix:</b> <code>/{prefixlen}</code></div>
                            <div><b>Address Scope:</b> <code>{address_scope}</code></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            except ValueError as err:
                st.error(f"⚠️ Invalid IPv4 CIDR input '{subnet_input}': {err}")
            except Exception as err:
                st.error(f"⚠️ Subnet calculation error: {err}")


# -----------------------------------------------------------------------------
# PAGE 4: SECURITY POLICY & ACL PLANNER
# -----------------------------------------------------------------------------
elif selected_page == "🔒 4. Security Policy & ACL Generator":
    st.markdown("""
        <div class="noc-header">
            <div>
                <h1 class="noc-title">🔒 Security Policy Matrix & Cisco IOS ACL Compiler</h1>
                <p class="noc-subtitle">ILLUSTRATIVE CISCO IOS EXTENDED ACL SCRIPT GENERATOR FOR CATALYST 3650</p>
            </div>
            <div class="noc-badge">Illustrative Template Generator</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 20px;">🛡️</span>
            <div>
                <div class="disclaimer-title">Security Policy & ACL Notice</div>
                The rules below represent <b>proposed security policies</b>.
                They are <b>NOT automatically applied</b> to Cisco Packet Tracer.
                The generator compiles active policy and VLAN rows into Cisco IOS commands as an <b>illustrative template</b> for <code>Multilayer Switch0</code>.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Section 1: Security Policies Table
    st.markdown("### 📜 Security Access Control Matrix")
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Edit rules below. The Cisco IOS ACL script automatically re-compiles from these exact rows.</p>", unsafe_allow_html=True)

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

    # Section 2: Dynamic Cisco IOS Extended ACL Script Generator
    st.markdown("### ⚙️ Dynamically Compiled Cisco IOS Extended ACL Script")
    st.markdown("""
        <p style="font-size: 12.5px; color: #94A3B8;">
            Generated directly from the rows of your active table above. Copy and paste into the CLI of <code>Multilayer Switch0</code>.
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
                <h1 class="noc-title">🧪 Network Validation Suite & Test Evidence Logs</h1>
                <p class="noc-subtitle">STRICT MANUAL AUDIT LOGS, CONFIRMED TESTS, AND CISCO TERMINAL INSPECTOR</p>
            </div>
            <div class="noc-badge">Strict Evidence Mode</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="disclaimer-banner">
            <span style="font-size: 20px;">🔬</span>
            <div>
                <div class="disclaimer-title">Strict Verification Protocol</div>
                <b>No test is marked as PASS unless verified by screenshot evidence or terminal execution.</b>
                Only confirmed tests (PC0 to 192.168.10.1 gateway ping and PC0 to 192.168.20.3 cross-subnet ping) are prepopulated as PASS.
                All other checks are initialized to <b>NOT TESTED</b>.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Verification Progress Metric Cards
    stats = data_manager.get_test_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Test Items</div>
                <div class="metric-value">{stats['total']}</div>
                <div class="metric-sub">Across 8 Categories</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #10B981;">
                <div class="metric-label" style="color: #10B981;">Confirmed PASS</div>
                <div class="metric-value" style="color: #10B981;">{stats['passed']}</div>
                <div class="metric-sub">Verified in PT Screenshots</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #F59E0B;">
                <div class="metric-label" style="color: #F59E0B;">NOT TESTED / PENDING</div>
                <div class="metric-value" style="color: #F59E0B;">{stats['untested']}</div>
                <div class="metric-sub">Awaiting CLI Execution</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #EF4444;">
                <div class="metric-label" style="color: #EF4444;">FAIL</div>
                <div class="metric-value" style="color: #EF4444;">{stats['failed']}</div>
                <div class="metric-sub">Requiring Fix in Topology</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 22px;'></div>", unsafe_allow_html=True)

    # Tabs: Interactive Checklist vs CLI Inspector vs CLI References
    tab_tests, tab_inspector, tab_cli_ref = st.tabs([
        "📋 Interactive Test Checklist & Evidence Recorder",
        "🔍 Cisco CLI Output Inspector",
        "📖 Cisco Catalyst CLI Reference Guide"
    ])

    # TAB 1: Interactive Checklist
    with tab_tests:
        st.markdown("### 📝 Record Verified Test Results")
        st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Update the status of each test item below after executing the corresponding command in Cisco Packet Tracer.</p>", unsafe_allow_html=True)

        for i, test in enumerate(st.session_state.test_checklist):
            status = test.get("status", "NOT TESTED")
            status_color = "#10B981" if status == "PASS" else ("#EF4444" if status == "FAIL" else "#F59E0B")
            
            with st.expander(f"**[{test['id']}] {test['title']}** — Status: **{status}** ({test['category']})", expanded=(status == "NOT TESTED")):
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
                    st.markdown(f"**Evidence Source:** `{test.get('source', 'Manual Entry')}`")
                
                with col_t2:
                    st.markdown("**Record Test Result:**")
                    new_status = st.selectbox(
                        "Outcome",
                        ["NOT TESTED", "PASS", "FAIL"],
                        index=["NOT TESTED", "PASS", "FAIL"].index(status) if status in ["NOT TESTED", "PASS", "FAIL"] else 0,
                        key=f"status_select_{test['id']}"
                    )

                    new_notes = st.text_area(
                        "Verification Notes / Terminal Output Evidence",
                        value=test.get("notes", ""),
                        height=80,
                        key=f"notes_input_{test['id']}"
                    )

                    if st.button("💾 Save Test Result", key=f"btn_save_{test['id']}"):
                        st.session_state.test_checklist[i]["status"] = new_status
                        st.session_state.test_checklist[i]["notes"] = new_notes
                        st.session_state.test_checklist[i]["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.test_checklist[i]["source"] = "Manual Verification"
                        st.success(f"Updated {test['id']} to {new_status}!")
                        st.rerun()

                st.markdown(f"<div style='font-size: 11px; color: #64748B; margin-top: 6px;'>Evidence Timestamp: {test.get('timestamp', 'Never')}</div>", unsafe_allow_html=True)

        st.markdown("---")
        
        # Test Log Table & Export
        st.markdown("### 📊 Test Logs Summary Table")
        raw_test_df = pd.DataFrame(st.session_state.test_checklist)
        expected_cols = ["id", "category", "title", "cisco_cmd", "status", "source", "timestamp", "notes"]
        for c in expected_cols:
            if c not in raw_test_df.columns:
                raw_test_df[c] = "Manual Verification" if c == "source" else "Not Specified"
        test_df = raw_test_df[expected_cols]
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
            if st.button("⚠️ Reset All Tests to Initial Evidence"):
                st.session_state.test_checklist = data_manager.get_initial_test_checklist()
                st.success("Test logs reset to initial verified evidence.")
                st.rerun()

    # TAB 2: Cisco CLI Output Inspector
    with tab_inspector:
        st.markdown("### 🔍 Terminal Output Inspector")
        st.markdown("""
            <p style="font-size: 12.5px; color: #94A3B8;">
                Paste terminal output copied from Cisco Packet Tracer below (or load verified sample evidence) to inspect for validation proof.
            </p>
        """, unsafe_allow_html=True)

        sample_choice = st.selectbox(
            "Load Verified Packet Tracer Sample Output",
            ["-- Select or Paste Custom Output --"] + list(cisco_helpers.SAMPLE_CLI_OUTPUTS.keys())
        )

        default_text = ""
        if sample_choice in cisco_helpers.SAMPLE_CLI_OUTPUTS:
            default_text = cisco_helpers.SAMPLE_CLI_OUTPUTS[sample_choice]

        user_cli_text = st.text_area(
            "Terminal Output Text",
            value=default_text,
            height=200,
            placeholder="Paste output from: ipconfig, ping, show vlan brief, show interfaces trunk..."
        )

        if st.button("🔎 Inspect Terminal Output"):
            analysis = cisco_helpers.parse_cisco_output(user_cli_text)
            badge_color = "#10B981" if analysis["status"] == "Success" else ("#EF4444" if analysis["status"] == "Alert" else "#F59E0B")
            
            st.markdown(f"""
                <div style="background: #111A2E; border: 1px solid #1E293B; border-radius: 8px; padding: 16px; margin-top: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 700; color: #FFFFFF;">Detected: <code>{analysis['detected_type']}</code></span>
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
                st.markdown("<p style='font-size: 12px; font-weight: 700; color: #94A3B8; margin-top: 10px;'>EXTRACTED EVIDENCE DETAILS:</p>", unsafe_allow_html=True)
                for item in analysis["details"]:
                    st.markdown(f"- `{item}`")

    # TAB 3: Cisco Commands Reference Guide
    with tab_cli_ref:
        st.markdown("### 📖 Cisco Catalyst Configuration & Verification Cheatsheet")
        st.markdown("<p style='font-size: 12px; color: #94A3B8;'>Verified commands used for configuring and verifying the NetSecure architecture in Cisco Packet Tracer.</p>", unsafe_allow_html=True)

        for topic, content in cisco_helpers.CISCO_CLI_REFERENCES.items():
            with st.expander(f"📌 {topic} ({content['device']})"):
                st.markdown(f"**Target Device:** `{content['device']}`")
                st.markdown("**Configuration Commands:**")
                st.code(content['commands'], language="cisco")
                st.markdown(f"**Verification CLI Command:** `{content['verification']}`")

"""
NetSecure - Data Manager and State Handler
Handles initial data structures, session state persistence, CSV export, and validation logic.
"""

import pandas as pd
import streamlit as st
from datetime import datetime

# Department Definitions matching Cisco Packet Tracer zones
DEPARTMENTS = {
    "Purple": {
        "name": "IT & Engineering",
        "vlan_id": 10,
        "color_hex": "#A855F7",
        "bg_hex": "rgba(168, 85, 247, 0.15)",
        "border_hex": "#9333EA",
        "switch": "Switch0",
        "pcs": ["PC0", "PC1"],
        "server": "Server0",
        "subnet_example": "192.168.10.0/24",
        "gateway_example": "192.168.10.1",
        "role": "Network administration, infrastructure management, and technical systems."
    },
    "Yellow": {
        "name": "Human Resources & Admin",
        "vlan_id": 20,
        "color_hex": "#EAB308",
        "bg_hex": "rgba(234, 179, 8, 0.15)",
        "border_hex": "#CA8A04",
        "switch": "Switch1",
        "pcs": ["PC2", "PC3"],
        "server": "Server1",
        "subnet_example": "192.168.20.0/24",
        "gateway_example": "192.168.20.1",
        "role": "Personnel records, recruitment, employee communications, and payroll coordination."
    },
    "Pink": {
        "name": "Finance & Accounting",
        "vlan_id": 30,
        "color_hex": "#EC4899",
        "bg_hex": "rgba(236, 72, 153, 0.15)",
        "border_hex": "#DB2777",
        "switch": "Switch2",
        "pcs": ["PC4", "PC5"],
        "server": "Server2",
        "subnet_example": "192.168.30.0/24",
        "gateway_example": "192.168.30.1",
        "role": "Financial audits, billing, budget control, and secure transactions."
    }
}

def get_initial_vlans_df():
    """Returns initial editable VLAN configuration DataFrame."""
    return pd.DataFrame([
        {
            "Department": "IT & Engineering (Purple Zone)",
            "VLAN_ID": 10,
            "Network_Address": "192.168.10.0/24",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.10.1",
            "Assigned_Switch": "Switch0",
            "Assigned_Devices": "PC0, PC1, Server0",
            "VLAN_Status": "Active (Example Config)",
            "InterVLAN_Routing": "Enabled (SVI on MLS0)"
        },
        {
            "Department": "HR & Admin (Yellow Zone)",
            "VLAN_ID": 20,
            "Network_Address": "192.168.20.0/24",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.20.1",
            "Assigned_Switch": "Switch1",
            "Assigned_Devices": "PC2, PC3, Server1",
            "VLAN_Status": "Active (Example Config)",
            "InterVLAN_Routing": "Enabled (SVI on MLS0)"
        },
        {
            "Department": "Finance & Accounting (Pink Zone)",
            "VLAN_ID": 30,
            "Network_Address": "192.168.30.0/24",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.30.1",
            "Assigned_Switch": "Switch2",
            "Assigned_Devices": "PC4, PC5, Server2",
            "VLAN_Status": "Active (Example Config)",
            "InterVLAN_Routing": "Enabled (SVI on MLS0)"
        }
    ])

def get_initial_endpoints_df():
    """Returns initial endpoint device IP allocation table."""
    return pd.DataFrame([
        # Purple Zone
        {"Device_Name": "PC0", "Department": "IT & Engineering", "VLAN_ID": 10, "IP_Address": "192.168.10.11", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.10.1", "Connected_Switch": "Switch0", "Switch_Port": "Fa0/1", "Config_Type": "DHCP / Static", "Verification_Status": "Untested"},
        {"Device_Name": "PC1", "Department": "IT & Engineering", "VLAN_ID": 10, "IP_Address": "192.168.10.12", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.10.1", "Connected_Switch": "Switch0", "Switch_Port": "Fa0/2", "Config_Type": "DHCP / Static", "Verification_Status": "Untested"},
        {"Device_Name": "Server0", "Department": "IT & Engineering", "VLAN_ID": 10, "IP_Address": "192.168.10.100", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.10.1", "Connected_Switch": "Switch0", "Switch_Port": "Fa0/10", "Config_Type": "Static (DNS/Web)", "Verification_Status": "Untested"},
        # Yellow Zone
        {"Device_Name": "PC2", "Department": "HR & Admin", "VLAN_ID": 20, "IP_Address": "192.168.20.11", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.20.1", "Connected_Switch": "Switch1", "Switch_Port": "Fa0/1", "Config_Type": "DHCP / Static", "Verification_Status": "Untested"},
        {"Device_Name": "PC3", "Department": "HR & Admin", "VLAN_ID": 20, "IP_Address": "192.168.20.12", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.20.1", "Connected_Switch": "Switch1", "Switch_Port": "Fa0/2", "Config_Type": "DHCP / Static", "Verification_Status": "Untested"},
        {"Device_Name": "Server1", "Department": "HR & Admin", "VLAN_ID": 20, "IP_Address": "192.168.20.100", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.20.1", "Connected_Switch": "Switch1", "Switch_Port": "Fa0/10", "Config_Type": "Static (HR Portal)", "Verification_Status": "Untested"},
        # Pink Zone
        {"Device_Name": "PC4", "Department": "Finance & Accounting", "VLAN_ID": 30, "IP_Address": "192.168.30.11", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.30.1", "Connected_Switch": "Switch2", "Switch_Port": "Fa0/1", "Config_Type": "DHCP / Static", "Verification_Status": "Untested"},
        {"Device_Name": "PC5", "Department": "Finance & Accounting", "VLAN_ID": 30, "IP_Address": "192.168.30.12", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.30.1", "Connected_Switch": "Switch2", "Switch_Port": "Fa0/2", "Config_Type": "DHCP / Static", "Verification_Status": "Untested"},
        {"Device_Name": "Server2", "Department": "Finance & Accounting", "VLAN_ID": 30, "IP_Address": "192.168.30.100", "Subnet_Mask": "255.255.255.0", "Gateway": "192.168.30.1", "Connected_Switch": "Switch2", "Switch_Port": "Fa0/10", "Config_Type": "Static (Accounting DB)", "Verification_Status": "Untested"},
    ])

def get_initial_security_policies_df():
    """Returns initial security access control policies."""
    return pd.DataFrame([
        {
            "Rule_ID": "SEC-01",
            "Source": "IT (VLAN 10)",
            "Destination": "All VLANs (10, 20, 30)",
            "Action": "Permit",
            "Protocol_Service": "SSH (TCP 22), HTTPS (443), ICMP",
            "Purpose": "IT administrative management & infrastructure support across departments",
            "Verification_Status": "Untested"
        },
        {
            "Rule_ID": "SEC-02",
            "Source": "HR (VLAN 20)",
            "Destination": "Finance (VLAN 30)",
            "Action": "Deny",
            "Protocol_Service": "IP (All Traffic)",
            "Purpose": "Strict departmental isolation; prevent unauthorized access to confidential ledger records",
            "Verification_Status": "Untested"
        },
        {
            "Rule_ID": "SEC-03",
            "Source": "Finance (VLAN 30)",
            "Destination": "HR (VLAN 20)",
            "Action": "Deny",
            "Protocol_Service": "IP (All Traffic)",
            "Purpose": "Prevent finance users from accessing employee personnel records",
            "Verification_Status": "Untested"
        },
        {
            "Rule_ID": "SEC-04",
            "Source": "HR (VLAN 20)",
            "Destination": "Server1 (192.168.20.100)",
            "Action": "Permit",
            "Protocol_Service": "HTTP (TCP 80), HTTPS (443)",
            "Purpose": "Allow HR workstations to access dedicated departmental HR web server",
            "Verification_Status": "Untested"
        },
        {
            "Rule_ID": "SEC-05",
            "Source": "Finance (VLAN 30)",
            "Destination": "Server2 (192.168.30.100)",
            "Action": "Permit",
            "Protocol_Service": "HTTPS (TCP 443), SQL (TCP 1433)",
            "Purpose": "Permit authorized financial workstations to reach accounting database server",
            "Verification_Status": "Untested"
        },
        {
            "Rule_ID": "SEC-06",
            "Source": "All Endpoints",
            "Destination": "Server0 (192.168.10.100)",
            "Action": "Permit",
            "Protocol_Service": "DNS (UDP 53), ICMP Echo",
            "Purpose": "Allow network-wide domain name resolution and basic network reachability check",
            "Verification_Status": "Untested"
        },
        {
            "Rule_ID": "SEC-07",
            "Source": "Access Switch Ports",
            "Destination": "Unregistered MACs",
            "Action": "Deny (Shutdown)",
            "Protocol_Service": "Ethernet Layer 2 (Port-Security)",
            "Purpose": "Restrict unauthorized rogue laptops connecting to wall ports",
            "Verification_Status": "Untested"
        }
    ])

def get_initial_test_checklist():
    """Returns verification checklist with real Cisco CLI validation commands."""
    return [
        {
            "id": "TEST-01",
            "category": "VLAN Verification",
            "title": "VLAN Database & Port Allocation",
            "description": "Confirm VLANs 10, 20, 30 are configured on Multilayer Switch0 and access switches (Switch0, Switch1, Switch2). Verify user ports are assigned to correct access VLANs.",
            "cisco_cmd": "show vlan brief",
            "expected_outcome": "VLANs 10 (IT), 20 (HR), 30 (Finance) show status 'active' and associated access ports Fa0/1-Fa0/10.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Verify on Switch0, Switch1, Switch2, and Multilayer Switch0."
        },
        {
            "id": "TEST-02",
            "category": "Trunk Verification",
            "title": "802.1Q Trunk Link Integrity",
            "description": "Verify trunk connections between Multilayer Switch0 and Switch0, Switch1, Switch2. Ensure 802.1Q encapsulation is active and VLANs 10, 20, 30 are allowed across trunks.",
            "cisco_cmd": "show interfaces trunk",
            "expected_outcome": "Trunk interfaces (e.g. Gig1/0/1-3) mode is 'on' or 'desirable', encapsulation is '802.1q', status is 'trunking'.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Check allowed VLANs list includes 10, 20, 30."
        },
        {
            "id": "TEST-03",
            "category": "Gateway & SVI Verification",
            "title": "Switch Virtual Interfaces (SVIs) Status",
            "description": "Verify that VLAN virtual interfaces (interface Vlan10, Vlan20, Vlan30) on Multilayer Switch0 are configured with appropriate gateway IP addresses and are UP/UP.",
            "cisco_cmd": "show ip interface brief",
            "expected_outcome": "Vlan10, Vlan20, Vlan30 interfaces have Status 'up' and Protocol 'up' with respective .1 gateway IPs.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Ensure 'ip routing' is enabled globally on Multilayer Switch0."
        },
        {
            "id": "TEST-04",
            "category": "Routing Verification",
            "title": "Inter-VLAN IP Routing Table",
            "description": "Verify that Multilayer Switch0 has active routing enabled and directly connected routes exist for all three departmental subnets.",
            "cisco_cmd": "show ip route",
            "expected_outcome": "Routing table shows 'C' (connected) routes for 192.168.10.0/24, 192.168.20.0/24, and 192.168.30.0/24.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Without 'ip routing', inter-VLAN communication will fail."
        },
        {
            "id": "TEST-05",
            "category": "DHCP Verification",
            "title": "DHCP Pool Binding / Address Lease",
            "description": "Confirm workstations (PC0 through PC5) receive valid IP configuration, subnet mask, and default gateway automatically from DHCP pool or static assignment.",
            "cisco_cmd": "show ip dhcp binding\nshow ip dhcp pool",
            "expected_outcome": "Leased IP addresses listed under respective pools with active client MAC addresses.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Verify on endpoints using 'ipconfig' in PC command prompt."
        },
        {
            "id": "TEST-06",
            "category": "Connectivity Testing",
            "title": "Default Gateway Reachability (Intra-VLAN Ping)",
            "description": "From PC0 ping 192.168.10.1; from PC2 ping 192.168.20.1; from PC4 ping 192.168.30.1 to verify access switch to MLS gateway link.",
            "cisco_cmd": "ping 192.168.10.1 (from PC0 command prompt)",
            "expected_outcome": "4 packets transmitted, 4 received (Reply from 192.168.10.1: bytes=32 time<1ms TTL=255).",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Initial packet may ARP-timeout; subsequent 3 should reply."
        },
        {
            "id": "TEST-07",
            "category": "Connectivity Testing",
            "title": "Intra-Department PC-to-Server Reachability",
            "description": "Test connectivity between workstations and their respective department servers (PC0 to Server0, PC2 to Server1, PC4 to Server2).",
            "cisco_cmd": "ping 192.168.10.100\nping 192.168.20.100\nping 192.168.30.100",
            "expected_outcome": "Successful ping replies with 0% packet loss.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Verifies local Layer 2 switching within the same VLAN."
        },
        {
            "id": "TEST-08",
            "category": "ACL Testing",
            "title": "Department Isolation ACL Verification (HR to Finance Deny)",
            "description": "Attempt to ping Finance PC4 (192.168.30.11) or Server2 (192.168.30.100) from HR PC2 (192.168.20.11). ACL rule SEC-02 should block this traffic.",
            "cisco_cmd": "ping 192.168.30.11 (from PC2)\nshow access-lists",
            "expected_outcome": "'Destination host unreachable' or 'Request timed out'. Packet hit counter increments on Cisco ACL.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Must confirm rule drops unauthorized traffic while permitted traffic flows."
        },
        {
            "id": "TEST-09",
            "category": "ACL Testing",
            "title": "IT Administrative Cross-VLAN Access (Permit Rule)",
            "description": "Verify IT PC0 (192.168.10.11) can reach Server1 (192.168.20.100) and Server2 (192.168.30.100) on permitted admin services.",
            "cisco_cmd": "ping 192.168.20.100\nshow access-lists",
            "expected_outcome": "Ping success, confirmed by matching permit rule in show access-lists counter.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Verifies rule SEC-01 administrative override."
        },
        {
            "id": "TEST-10",
            "category": "Port Security",
            "title": "Switch Port Security Enforcement",
            "description": "Verify port-security settings on access ports to prevent MAC spoofing and rogue device connection.",
            "cisco_cmd": "show port-security interface fa0/1\nshow port-security address",
            "expected_outcome": "Port Security: Enabled, Port Status: Secure-up, Violation Mode: Shutdown or Restrict.",
            "status": "Not Tested",
            "timestamp": "Not Run",
            "notes": "Test on Switch0, Switch1, Switch2 access ports."
        }
    ]

def init_session_state():
    """Initializes Streamlit session state if keys are not present."""
    if "vlans_df" not in st.session_state:
        st.session_state.vlans_df = get_initial_vlans_df()
        
    if "endpoints_df" not in st.session_state:
        st.session_state.endpoints_df = get_initial_endpoints_df()
        
    if "security_policies_df" not in st.session_state:
        st.session_state.security_policies_df = get_initial_security_policies_df()
        
    if "test_checklist" not in st.session_state:
        st.session_state.test_checklist = get_initial_test_checklist()

def get_test_stats():
    """Computes summary metrics for validation tests."""
    tests = st.session_state.get("test_checklist", [])
    total = len(tests)
    passed = sum(1 for t in tests if t["status"] == "Passed")
    failed = sum(1 for t in tests if t["status"] == "Failed")
    untested = sum(1 for t in tests if t["status"] in ["Not Tested", "In Progress", "Unverified"])
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "untested": untested,
        "pass_rate": round((passed / total * 100) if total > 0 else 0, 1)
    }

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Converts a pandas DataFrame into utf-8 encoded CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')

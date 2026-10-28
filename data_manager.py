"""
NetSecure - Data Manager and State Handler
Centralizes network device, VLAN, IP addressing, security policies, and validation test logs.
Accurately reflects verified facts from Cisco Packet Tracer project screenshots:
  - Multilayer Switch0 (Cisco 3650 Core MLS)
  - Access Switches: Switch0, Switch1, Switch2
  - VLAN 10: Management (192.168.10.0/24, GW 192.168.10.1)
  - VLAN 20: finance (192.168.20.0/24, GW 192.168.20.1, DNS 8.8.8.8)
  - VLAN 30: IT (192.168.30.0/24, GW 192.168.30.1, DNS 8.8.8.8)
  - Verified Endpoints: PC0 (192.168.10.3), PC2 (192.168.20.3)
  - Confirmed Tests: PC0 -> 192.168.10.1 (PASS), PC0 -> 192.168.20.3 (PASS)
"""

import pandas as pd
import streamlit as st
from datetime import datetime

# Verified Department Definitions matching Cisco Packet Tracer project
DEPARTMENTS = {
    "Purple": {
        "name": "Management",
        "vlan_id": 10,
        "color_hex": "#A855F7",
        "bg_hex": "rgba(168, 85, 247, 0.15)",
        "border_hex": "#9333EA",
        "switch": "Switch0",
        "pcs": ["PC0", "PC1"],
        "server": "Server0",
        "subnet": "192.168.10.0/24",
        "gateway": "192.168.10.1",
        "dns": "Not specified in pool",
        "verified_devices": ["PC0 (192.168.10.3)"],
        "unverified_devices": ["PC1", "Server0"],
        "role": "Administrative network management, device control, and infrastructure supervision."
    },
    "Yellow": {
        "name": "finance",
        "vlan_id": 20,
        "color_hex": "#EAB308",
        "bg_hex": "rgba(234, 179, 8, 0.15)",
        "border_hex": "#CA8A04",
        "switch": "Switch1",
        "pcs": ["PC2", "PC3"],
        "server": "Server1",
        "subnet": "192.168.20.0/24",
        "gateway": "192.168.20.1",
        "dns": "8.8.8.8",
        "verified_devices": ["PC2 (192.168.20.3)"],
        "unverified_devices": ["PC3", "Server1"],
        "role": "Financial records, budget ledgers, transactions, and audit systems."
    },
    "Pink": {
        "name": "IT",
        "vlan_id": 30,
        "color_hex": "#EC4899",
        "bg_hex": "rgba(236, 72, 153, 0.15)",
        "border_hex": "#DB2777",
        "switch": "Switch2",
        "pcs": ["PC4", "PC5"],
        "server": "Server2",
        "subnet": "192.168.30.0/24",
        "gateway": "192.168.30.1",
        "dns": "8.8.8.8",
        "verified_devices": [],
        "unverified_devices": ["PC4", "PC5", "Server2"],
        "role": "Internal IT technical services, helpdesk support, and system administration."
    }
}

def get_initial_vlans_df():
    """
    Returns verified VLAN configuration DataFrame based on Packet Tracer configuration.
    VLAN 10 = Management, VLAN 20 = finance, VLAN 30 = IT.
    """
    return pd.DataFrame([
        {
            "Department_Zone": "Purple Zone",
            "VLAN_ID": 10,
            "VLAN_Name": "Management",
            "Network_Address": "192.168.10.0/24",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.10.1",
            "DNS_Server": "Not specified in pool",
            "Assigned_Switch": "Switch0",
            "Verified_Port_Sample": "Fa0/1 (Verified on sample switch)",
            "Config_Status": "VERIFIED in Packet Tracer"
        },
        {
            "Department_Zone": "Yellow Zone",
            "VLAN_ID": 20,
            "VLAN_Name": "finance",
            "Network_Address": "192.168.20.0/24",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.20.1",
            "DNS_Server": "8.8.8.8",
            "Assigned_Switch": "Switch1",
            "Verified_Port_Sample": "Fa0/2 (Verified on sample switch)",
            "Config_Status": "VERIFIED in Packet Tracer"
        },
        {
            "Department_Zone": "Pink Zone",
            "VLAN_ID": 30,
            "VLAN_Name": "IT",
            "Network_Address": "192.168.30.0/24",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.30.1",
            "DNS_Server": "8.8.8.8",
            "Assigned_Switch": "Switch2",
            "Verified_Port_Sample": "Fa0/3 (Verified on sample switch)",
            "Config_Status": "VERIFIED in Packet Tracer"
        }
    ])

def get_initial_endpoints_df():
    """
    Returns endpoint device IP allocation table.
    Explicitly distinguishes verified IPs (PC0, PC2) from unverified endpoints.
    """
    return pd.DataFrame([
        # Purple Zone: Management (VLAN 10)
        {
            "Device_Name": "PC0",
            "Department": "Management",
            "VLAN_ID": 10,
            "IPv4_Address": "192.168.10.3",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.10.1",
            "Connected_Switch": "Switch0",
            "Switch_Port": "Fa0/1 (Verified on sample switch)",
            "IP_Allocation": "DHCP (Verified)",
            "Verification_Status": "VERIFIED",
            "Evidence": "Verified from PC0 ipconfig & ping screenshots"
        },
        {
            "Device_Name": "PC1",
            "Department": "Management",
            "VLAN_ID": 10,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.10.1",
            "Connected_Switch": "Switch0",
            "Switch_Port": "Unverified",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Not configured/confirmed in Packet Tracer evidence"
        },
        {
            "Device_Name": "Server0",
            "Department": "Management",
            "VLAN_ID": 10,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.10.1",
            "Connected_Switch": "Switch0",
            "Switch_Port": "Unverified",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Server IP and reachability not confirmed"
        },
        # Yellow Zone: finance (VLAN 20)
        {
            "Device_Name": "PC2",
            "Department": "finance",
            "VLAN_ID": 20,
            "IPv4_Address": "192.168.20.3",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.20.1",
            "Connected_Switch": "Switch1",
            "Switch_Port": "Fa0/2 (Verified on sample switch)",
            "IP_Allocation": "DHCP (Verified)",
            "Verification_Status": "VERIFIED",
            "Evidence": "Verified from PC2 ipconfig screenshot"
        },
        {
            "Device_Name": "PC3",
            "Department": "finance",
            "VLAN_ID": 20,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.20.1",
            "Connected_Switch": "Switch1",
            "Switch_Port": "Unverified",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Not configured/confirmed in Packet Tracer evidence"
        },
        {
            "Device_Name": "Server1",
            "Department": "finance",
            "VLAN_ID": 20,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.20.1",
            "Connected_Switch": "Switch1",
            "Switch_Port": "Unverified",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Server IP and reachability not confirmed"
        },
        # Pink Zone: IT (VLAN 30)
        {
            "Device_Name": "PC4",
            "Department": "IT",
            "VLAN_ID": 30,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.30.1",
            "Connected_Switch": "Switch2",
            "Switch_Port": "Fa0/3 (Verified on sample switch)",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Not configured/confirmed in Packet Tracer evidence"
        },
        {
            "Device_Name": "PC5",
            "Department": "IT",
            "VLAN_ID": 30,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.30.1",
            "Connected_Switch": "Switch2",
            "Switch_Port": "Unverified",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Not configured/confirmed in Packet Tracer evidence"
        },
        {
            "Device_Name": "Server2",
            "Department": "IT",
            "VLAN_ID": 30,
            "IPv4_Address": "Unverified / Not configured",
            "Subnet_Mask": "255.255.255.0",
            "Default_Gateway": "192.168.30.1",
            "Connected_Switch": "Switch2",
            "Switch_Port": "Unverified",
            "IP_Allocation": "Not configured/confirmed",
            "Verification_Status": "UNVERIFIED",
            "Evidence": "Server IP and reachability not confirmed"
        }
    ])

def get_initial_security_policies_df():
    """
    Returns initial proposed security access control policies.
    All policies are initialized to NOT TESTED.
    """
    return pd.DataFrame([
        {
            "Rule_ID": "SEC-01",
            "Source": "Management (192.168.10.0/24)",
            "Destination": "Any",
            "Action": "Permit",
            "Protocol": "IP",
            "Port_Service": "Any",
            "Purpose": "Administrative management access across all subnets",
            "Verification_Status": "NOT TESTED"
        },
        {
            "Rule_ID": "SEC-02",
            "Source": "finance (192.168.20.0/24)",
            "Destination": "IT (192.168.30.0/24)",
            "Action": "Deny",
            "Protocol": "IP",
            "Port_Service": "Any",
            "Purpose": "Inter-department isolation: restrict finance traffic to IT subnet",
            "Verification_Status": "NOT TESTED"
        },
        {
            "Rule_ID": "SEC-03",
            "Source": "IT (192.168.30.0/24)",
            "Destination": "finance (192.168.20.0/24)",
            "Action": "Deny",
            "Protocol": "IP",
            "Port_Service": "Any",
            "Purpose": "Inter-department isolation: restrict IT traffic to finance records",
            "Verification_Status": "NOT TESTED"
        },
        {
            "Rule_ID": "SEC-04",
            "Source": "finance (192.168.20.0/24)",
            "Destination": "Server1 (192.168.20.0/24)",
            "Action": "Permit",
            "Protocol": "TCP",
            "Port_Service": "80, 443",
            "Purpose": "Permit finance workstations to access departmental web portal",
            "Verification_Status": "NOT TESTED"
        },
        {
            "Rule_ID": "SEC-05",
            "Source": "IT (192.168.30.0/24)",
            "Destination": "Server2 (192.168.30.0/24)",
            "Action": "Permit",
            "Protocol": "TCP",
            "Port_Service": "80, 443",
            "Purpose": "Permit IT workstations to access departmental IT server",
            "Verification_Status": "NOT TESTED"
        },
        {
            "Rule_ID": "SEC-06",
            "Source": "All Endpoints",
            "Destination": "DNS Server (8.8.8.8)",
            "Action": "Permit",
            "Protocol": "UDP",
            "Port_Service": "53",
            "Purpose": "Allow domain name resolution configured in DHCP pools",
            "Verification_Status": "NOT TESTED"
        }
    ])

def get_initial_test_checklist():
    """
    Returns verification checklist.
    PREPOPULATES ONLY THESE TWO CONFIRMED TESTS AS 'PASS':
      1. PC0 -> 192.168.10.1: 4/4 replies, 0% packet loss (Default Gateway).
      2. PC0 -> 192.168.20.3: 4/4 replies, 0% packet loss (Cross-Subnet Reachability).
    EVERY OTHER TEST IS INITIALIZED TO 'NOT TESTED'.
    """
    return [
        {
            "id": "TEST-01",
            "category": "Connectivity Testing",
            "title": "PC0 to 192.168.10.1 (Default Gateway)",
            "description": "Ping 192.168.10.1 from PC0 command prompt to verify local default gateway reachability.",
            "cisco_cmd": "ping 192.168.10.1",
            "expected_outcome": "4/4 replies, 0% packet loss. Reply from 192.168.10.1: bytes=32 time<1ms.",
            "status": "PASS",
            "source": "PC0 Terminal Screenshot",
            "timestamp": "Verified from Project Screenshot",
            "notes": "Verified PASS in Packet Tracer screenshot: 4/4 replies, 0% packet loss (Sent = 4, Received = 4, Lost = 0)."
        },
        {
            "id": "TEST-02",
            "category": "Connectivity Testing",
            "title": "PC0 to 192.168.20.3 (Cross-Subnet Reachability)",
            "description": "Ping 192.168.20.3 from PC0. Demonstrates cross-subnet reachability from 192.168.10.0/24 to 192.168.20.0/24.",
            "cisco_cmd": "ping 192.168.20.3",
            "expected_outcome": "4/4 replies, 0% packet loss. Reply from 192.168.20.3: bytes=32.",
            "status": "PASS",
            "source": "PC0 Terminal Screenshot",
            "timestamp": "Verified from Project Screenshot",
            "notes": "Verified PASS in Packet Tracer screenshot: 4/4 replies, 0% packet loss. Confirms cross-subnet reachability to 192.168.20.0/24 (destination IP matches PC2)."
        },
        {
            "id": "TEST-03",
            "category": "Connectivity Testing",
            "title": "PC2 Local Stack Self-Ping (192.168.20.3)",
            "description": "Ping 192.168.20.3 from PC2 to test local TCP/IP stack configuration.",
            "cisco_cmd": "ping 192.168.20.3 (from PC2)",
            "expected_outcome": "Replies from 192.168.20.3 with 0% loss.",
            "status": "NOT TESTED",
            "source": "PC2 Terminal Screenshot",
            "timestamp": "Not Run as Verified Network Check",
            "notes": "Self-ping test on PC2 received 4/4 on second attempt. Local interface check only; NOT an inter-VLAN test."
        },
        {
            "id": "TEST-04",
            "category": "VLAN Verification",
            "title": "VLAN Database Verification (All Switches)",
            "description": "Confirm VLANs 10 (Management), 20 (finance), and 30 (IT) exist and are active on Multilayer Switch0 and access switches Switch0, Switch1, Switch2.",
            "cisco_cmd": "show vlan brief",
            "expected_outcome": "VLAN 10 Management, VLAN 20 finance, VLAN 30 IT show status 'active'.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Verified on sample access switch (Fa0/1->10, Fa0/2->20, Fa0/3->30). Status on Multilayer Switch0 and other switches remains unverified."
        },
        {
            "id": "TEST-05",
            "category": "Trunk Verification",
            "title": "802.1Q Trunk Configuration & Allowed VLANs",
            "description": "Verify 802.1Q trunking on links between Multilayer Switch0 and access switches Switch0, Switch1, Switch2.",
            "cisco_cmd": "show interfaces trunk",
            "expected_outcome": "Encapsulation: 802.1q, Status: trunking, Native VLAN: 1, Allowed VLANs: 10,20,30.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Gig0/1 trunk verified on sample access switch. Trunk status on Multilayer Switch0 and other access switches remains unverified."
        },
        {
            "id": "TEST-06",
            "category": "Gateway & Interface Verification",
            "title": "Multilayer Switch0 SVIs UP/UP Status",
            "description": "Verify that VLAN virtual interfaces (Vlan10, Vlan20, Vlan30) on Multilayer Switch0 are configured with gateway IPs (.1) and are UP/UP.",
            "cisco_cmd": "show ip interface brief",
            "expected_outcome": "Interface Vlan10 (192.168.10.1), Vlan20 (192.168.20.1), Vlan30 (192.168.30.1) show Status: up, Protocol: up.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Central multilayer switch interface status requires confirmation in Packet Tracer."
        },
        {
            "id": "TEST-07",
            "category": "Routing Verification",
            "title": "Inter-VLAN IP Routing Table",
            "description": "Confirm 'ip routing' is enabled and connected routes exist for 192.168.10.0/24, 192.168.20.0/24, 192.168.30.0/24.",
            "cisco_cmd": "show ip route",
            "expected_outcome": "Routing table displays 'C' (connected) routes for subnets 10.0/24, 20.0/24, and 30.0/24.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Routing table on Multilayer Switch0 has not been verified from CLI output."
        },
        {
            "id": "TEST-08",
            "category": "DHCP Verification",
            "title": "DHCP Operation Across All VLANs",
            "description": "Confirm DHCP address leases for pools Management, finance, and IT.",
            "cisco_cmd": "show ip dhcp binding\nshow ip dhcp pool",
            "expected_outcome": "Active client bindings displayed for 192.168.10.0/24, 192.168.20.0/24, and 192.168.30.0/24.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Pools verified in switch configuration (prompt Switch>). Operation and leases across all VLANs require verification."
        },
        {
            "id": "TEST-09",
            "category": "Connectivity Testing",
            "title": "Server Reachability (Server0, Server1, Server2)",
            "description": "Verify reachability to departmental servers from corresponding workstations.",
            "cisco_cmd": "ping <server_ip>",
            "expected_outcome": "Successful ping replies from Server0, Server1, and Server2.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Server IP addresses and reachability remain unverified."
        },
        {
            "id": "TEST-10",
            "category": "Security / ACL Testing",
            "title": "Department Isolation ACL Enforcement",
            "description": "Verify that traffic from finance (VLAN 20) to IT (VLAN 30) is dropped after ACL configuration.",
            "cisco_cmd": "ping 192.168.30.x (from PC2)\nshow access-lists",
            "expected_outcome": "Packets denied / Request timed out. Deny hit counter increments on Multilayer Switch0 ACL.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "ACL rules are proposed; actual enforcement in Packet Tracer has not been tested."
        },
        {
            "id": "TEST-11",
            "category": "Security / Port Security",
            "title": "Switch Port Security Verification",
            "description": "Verify port-security settings on access switch ports to prevent unauthorized MAC connections.",
            "cisco_cmd": "show port-security interface fa0/1",
            "expected_outcome": "Port Security: Enabled, Port Status: Secure-up.",
            "status": "NOT TESTED",
            "source": "Pending",
            "timestamp": "Not Run",
            "notes": "Port security configuration on access switches has not been verified."
        }
    ]

def init_session_state():
    """Initializes Streamlit session state and refreshes if older cached session data is present."""
    if "vlans_df" not in st.session_state or "VLAN_Name" not in st.session_state.vlans_df.columns:
        st.session_state.vlans_df = get_initial_vlans_df()
        
    if ("endpoints_df" not in st.session_state or 
        "IPv4_Address" not in st.session_state.endpoints_df.columns or 
        any("192.168.10.x" in str(x) for x in st.session_state.endpoints_df.get("IPv4_Address", []))):
        st.session_state.endpoints_df = get_initial_endpoints_df()
        
    if "security_policies_df" not in st.session_state or "Protocol" not in st.session_state.security_policies_df.columns:
        st.session_state.security_policies_df = get_initial_security_policies_df()
        
    if ("test_checklist" not in st.session_state or 
        any("source" not in t for t in st.session_state.test_checklist) or
        any(t.get("id") == "TEST-03" and t.get("status") == "PASS" for t in st.session_state.test_checklist)):
        st.session_state.test_checklist = get_initial_test_checklist()

def get_test_stats():
    """Computes summary metrics for validation tests using PASS / FAIL / NOT TESTED."""
    tests = st.session_state.get("test_checklist", [])
    total = len(tests)
    passed = sum(1 for t in tests if t.get("status") == "PASS")
    failed = sum(1 for t in tests if t.get("status") == "FAIL")
    untested = sum(1 for t in tests if t.get("status") in ["NOT TESTED", "Not Tested", "Pending", "Unverified"])
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

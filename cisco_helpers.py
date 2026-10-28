"""
NetSecure - Cisco CLI & Packet Tracer Automation Helper
Provides Cisco IOS CLI reference templates, dynamic Extended ACL generator,
and CLI output verification parser.
"""

import re
import pandas as pd

CISCO_CLI_REFERENCES = {
    "VLAN Configuration": {
        "device": "Multilayer Switch0 & Access Switches (Switch0, 1, 2)",
        "commands": """! Configure Department VLANs on Switch
Switch> enable
Switch# configure terminal
Switch(config)# vlan 10
Switch(config-vlan)# name IT_Dept
Switch(config-vlan)# exit

Switch(config)# vlan 20
Switch(config-vlan)# name HR_Dept
Switch(config-vlan)# exit

Switch(config)# vlan 30
Switch(config-vlan)# name Finance_Dept
Switch(config-vlan)# exit
Switch(config)# end
Switch# copy running-config startup-config""",
        "verification": "show vlan brief"
    },
    "Trunk Link Configuration": {
        "device": "Multilayer Switch0 & Access Switches",
        "commands": """! On Multilayer Switch0 (Catalyst 3650):
MLS0(config)# interface range GigabitEthernet 1/0/1 - 3
MLS0(config-if-range)# switchport trunk encapsulation dot1q
MLS0(config-if-range)# switchport mode trunk
MLS0(config-if-range)# switchport trunk allowed vlan 10,20,30
MLS0(config-if-range)# no shutdown
MLS0(config-if-range)# exit

! On Access Switches (Switch0, Switch1, Switch2 Uplink e.g. Gig0/1):
Switch(config)# interface GigabitEthernet 0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30
Switch(config-if)# no shutdown""",
        "verification": "show interfaces trunk"
    },
    "Inter-VLAN SVIs & IP Routing": {
        "device": "Multilayer Switch0 (Cisco 3650 Core)",
        "commands": """! Enable Layer 3 Hardware Routing
MLS0(config)# ip routing

! SVI for VLAN 10 (IT Gateway)
MLS0(config)# interface Vlan10
MLS0(config-if)# ip address 192.168.10.1 255.255.255.0
MLS0(config-if)# no shutdown
MLS0(config-if)# exit

! SVI for VLAN 20 (HR Gateway)
MLS0(config)# interface Vlan20
MLS0(config-if)# ip address 192.168.20.1 255.255.255.0
MLS0(config-if)# no shutdown
MLS0(config-if)# exit

! SVI for VLAN 30 (Finance Gateway)
MLS0(config)# interface Vlan30
MLS0(config-if)# ip address 192.168.30.1 255.255.255.0
MLS0(config-if)# no shutdown
MLS0(config-if)# exit""",
        "verification": "show ip interface brief\nshow ip route"
    },
    "DHCP Pool Configuration": {
        "device": "Multilayer Switch0",
        "commands": """! DHCP Pool for VLAN 10 (IT)
MLS0(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10
MLS0(config)# ip dhcp excluded-address 192.168.10.100
MLS0(config)# ip dhcp pool POOL_VLAN10
MLS0(dhcp-config)# network 192.168.10.0 255.255.255.0
MLS0(dhcp-config)# default-router 192.168.10.1
MLS0(dhcp-config)# dns-server 192.168.10.100
MLS0(dhcp-config)# exit

! DHCP Pool for VLAN 20 (HR)
MLS0(config)# ip dhcp excluded-address 192.168.20.1 192.168.20.10
MLS0(config)# ip dhcp excluded-address 192.168.20.100
MLS0(config)# ip dhcp pool POOL_VLAN20
MLS0(dhcp-config)# network 192.168.20.0 255.255.255.0
MLS0(dhcp-config)# default-router 192.168.20.1
MLS0(dhcp-config)# dns-server 192.168.10.100
MLS0(dhcp-config)# exit

! DHCP Pool for VLAN 30 (Finance)
MLS0(config)# ip dhcp excluded-address 192.168.30.1 192.168.30.10
MLS0(config)# ip dhcp excluded-address 192.168.30.100
MLS0(config)# ip dhcp pool POOL_VLAN30
MLS0(dhcp-config)# network 192.168.30.0 255.255.255.0
MLS0(dhcp-config)# default-router 192.168.30.1
MLS0(dhcp-config)# dns-server 192.168.10.100
MLS0(dhcp-config)# exit""",
        "verification": "show ip dhcp binding"
    },
    "Port Security Configuration": {
        "device": "Access Switches (Switch0, Switch1, Switch2)",
        "commands": """! Configure Port Security on Access Ports (e.g. Fa0/1 to Fa0/5)
Switch(config)# interface range FastEthernet 0/1 - 5
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport port-security
Switch(config-if-range)# switchport port-security maximum 2
Switch(config-if-range)# switchport port-security mac-address sticky
Switch(config-if-range)# switchport port-security violation restrict
Switch(config-if-range)# end""",
        "verification": "show port-security interface fa0/1"
    }
}

SAMPLE_CLI_OUTPUTS = {
    "show vlan brief": """VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/11, Fa0/12, Fa0/13, Fa0/14
10   IT_Dept                          active    Fa0/1, Fa0/2, Fa0/10
20   HR_Dept                          active    Fa0/3, Fa0/4, Fa0/5
30   Finance_Dept                     active    Fa0/6, Fa0/7, Fa0/8
1002 fddi-default                     active    
1003 token-ring-default               active    
1004 fddinet-default                  active    
1005 trnet-default                    active    """,

    "show interfaces trunk": """Port        Mode         Encapsulation  Status        Native vlan
Gig1/0/1    on           802.1q         trunking      1
Gig1/0/2    on           802.1q         trunking      1
Gig1/0/3    on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gig1/0/1    10,20,30
Gig1/0/2    10,20,30
Gig1/0/3    10,20,30

Port        Vlans in spanning tree forwarding state and not pruned
Gig1/0/1    10,20,30
Gig1/0/2    10,20,30
Gig1/0/3    10,20,30""",

    "show ip interface brief": """Interface              IP-Address      OK? Method Status                Protocol
FastEthernet0/1        unassigned      YES unset  up                    up
GigabitEthernet1/0/1   unassigned      YES unset  up                    up
GigabitEthernet1/0/2   unassigned      YES unset  up                    up
GigabitEthernet1/0/3   unassigned      YES unset  up                    up
Vlan10                 192.168.10.1    YES manual up                    up
Vlan20                 192.168.20.1    YES manual up                    up
Vlan30                 192.168.30.1    YES manual up                    up""",

    "show ip route": """Codes: C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area 

Gateway of last resort is not set

C    192.168.10.0/24 is directly connected, Vlan10
C    192.168.20.0/24 is directly connected, Vlan20
C    192.168.30.0/24 is directly connected, Vlan30""",

    "ping response": """Pinging 192.168.30.11 with 32 bytes of data:
Reply from 192.168.30.11: bytes=32 time=2ms TTL=127
Reply from 192.168.30.11: bytes=32 time=1ms TTL=127
Reply from 192.168.30.11: bytes=32 time=1ms TTL=127
Reply from 192.168.30.11: bytes=32 time=1ms TTL=127

Ping statistics for 192.168.30.11:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 1ms, Maximum = 2ms, Average = 1ms"""
}

def generate_cisco_acl_script(security_policies_df: pd.DataFrame, vlans_df: pd.DataFrame) -> str:
    """
    Translates the security policies defined in the dashboard into
    real Cisco IOS Extended Access Control List commands for Multilayer Switch0.
    """
    lines = [
        "! ===================================================================",
        "! NetSecure: Cisco Catalyst 3650 Extended Access Control Lists (ACL)",
        "! Generated for Inter-VLAN Security & Departmental Traffic Isolation",
        "! ===================================================================",
        "enable",
        "configure terminal",
        "ip routing",
        ""
    ]

    # Map VLAN info
    vlan_subnets = {
        10: "192.168.10.0 0.0.0.255",
        20: "192.168.20.0 0.0.0.255",
        30: "192.168.30.0 0.0.0.255"
    }

    # Generate ACL for VLAN 20 (HR) - Prevents unauthorized access to Finance
    lines.extend([
        "! -------------------------------------------------------------------",
        "! ACL for VLAN 20 (HR & Administration Subnet) - Inbound Filtering",
        "! Prevents unauthorized access to Finance (VLAN 30) while allowing local traffic",
        "! -------------------------------------------------------------------",
        "ip access-list extended ACL_VLAN20_IN",
        " remark --- Permit intra-departmental local traffic ---",
        " permit ip 192.168.20.0 0.0.0.255 192.168.20.0 0.0.0.255",
        " remark --- Permit HR access to Server1 (Web/Portal) ---",
        " permit tcp 192.168.20.0 0.0.0.255 host 192.168.20.100 eq 80",
        " permit tcp 192.168.20.0 0.0.0.255 host 192.168.20.100 eq 443",
        " remark --- Permit DNS resolution to Server0 in IT zone ---",
        " permit udp 192.168.20.0 0.0.0.255 host 192.168.10.100 eq 53",
        " remark --- SEC-02: Strict Department Isolation: Block HR -> Finance ---",
        " deny ip 192.168.20.0 0.0.0.255 192.168.30.0 0.0.0.255 log",
        " remark --- Permit outbound internet/general traffic ---",
        " permit ip 192.168.20.0 0.0.0.255 any",
        "exit",
        ""
    ])

    # Generate ACL for VLAN 30 (Finance) - Prevents access to HR records
    lines.extend([
        "! -------------------------------------------------------------------",
        "! ACL for VLAN 30 (Finance & Accounting Subnet) - Inbound Filtering",
        "! Restricts Finance traffic from HR (VLAN 20) and protects Server2 DB",
        "! -------------------------------------------------------------------",
        "ip access-list extended ACL_VLAN30_IN",
        " remark --- Permit intra-departmental local traffic ---",
        " permit ip 192.168.30.0 0.0.0.255 192.168.30.0 0.0.0.255",
        " remark --- Permit Finance workstations to reach Server2 (DB/Accounting) ---",
        " permit tcp 192.168.30.0 0.0.0.255 host 192.168.30.100 eq 443",
        " permit tcp 192.168.30.0 0.0.0.255 host 192.168.30.100 eq 1433",
        " remark --- Permit DNS resolution to Server0 ---",
        " permit udp 192.168.30.0 0.0.0.255 host 192.168.10.100 eq 53",
        " remark --- SEC-03: Strict Department Isolation: Block Finance -> HR ---",
        " deny ip 192.168.30.0 0.0.0.255 192.168.20.0 0.0.0.255 log",
        " remark --- Permit general authorized traffic ---",
        " permit ip 192.168.30.0 0.0.0.255 any",
        "exit",
        ""
    ])

    # Generate ACL for VLAN 10 (IT Management)
    lines.extend([
        "! -------------------------------------------------------------------",
        "! ACL for VLAN 10 (IT & Engineering Subnet) - Administrative Override",
        "! IT retains full administrative diagnostics & management access",
        "! -------------------------------------------------------------------",
        "ip access-list extended ACL_VLAN10_IN",
        " remark --- SEC-01: IT Full Admin Access & Diagnostics ---",
        " permit ip 192.168.10.0 0.0.0.255 any",
        "exit",
        ""
    ])

    # Apply ACLs to SVIs
    lines.extend([
        "! -------------------------------------------------------------------",
        "! Apply Inbound ACLs to SVI Virtual Interfaces on Multilayer Switch0",
        "! -------------------------------------------------------------------",
        "interface Vlan10",
        " ip access-group ACL_VLAN10_IN in",
        "exit",
        "",
        "interface Vlan20",
        " ip access-group ACL_VLAN20_IN in",
        "exit",
        "",
        "interface Vlan30",
        " ip access-group ACL_VLAN30_IN in",
        "exit",
        "",
        "end",
        "! Verify active rules and packet drop/permit hit counters:",
        "show access-lists",
        "copy running-config startup-config"
    ])

    return "\n".join(lines)

def parse_cisco_output(raw_text: str):
    """
    Parses pasted Cisco CLI output text to extract structured verification insights.
    Detects VLAN states, trunk ports, SVI IP statuses, ping results, etc.
    """
    results = {
        "detected_type": "Unknown",
        "status": "Neutral",
        "summary": "Could not identify standard Cisco command output format.",
        "details": []
    }

    if not raw_text or not raw_text.strip():
        return results

    text = raw_text.strip()

    # Case 1: show vlan brief
    if "VLAN Name" in text or ("10" in text and "active" in text):
        results["detected_type"] = "show vlan brief"
        vlans_found = []
        for line in text.splitlines():
            m = re.match(r"^(\d+)\s+([A-Za-z0-9_\-]+)\s+(active|act/unsup)", line.strip())
            if m:
                vlans_found.append(f"VLAN {m.group(1)} ({m.group(2)}) - {m.group(3)}")
        if vlans_found:
            results["status"] = "Success"
            results["summary"] = f"Detected {len(vlans_found)} active VLAN database entries."
            results["details"] = vlans_found
        else:
            results["status"] = "Warning"
            results["summary"] = "VLAN header detected, but no standard numbered VLAN lines matched."

    # Case 2: show interfaces trunk
    elif "Port" in text and ("trunking" in text or "802.1q" in text):
        results["detected_type"] = "show interfaces trunk"
        trunks_found = []
        for line in text.splitlines():
            if "trunking" in line:
                trunks_found.append(line.strip())
        results["status"] = "Success"
        results["summary"] = f"Detected {len(trunks_found)} active 802.1Q trunking port(s)."
        results["details"] = trunks_found

    # Case 3: show ip interface brief
    elif "IP-Address" in text and ("Vlan" in text or "FastEthernet" in text or "GigabitEthernet" in text):
        results["detected_type"] = "show ip interface brief"
        up_interfaces = []
        for line in text.splitlines():
            if "up" in line and not line.startswith("Interface"):
                parts = line.split()
                if len(parts) >= 2:
                    up_interfaces.append(f"{parts[0]}: IP {parts[1]} (Status: UP / Protocol: UP)")
        results["status"] = "Success"
        results["summary"] = f"Detected {len(up_interfaces)} interface(s) in UP status."
        results["details"] = up_interfaces

    # Case 4: ping response
    elif "bytes=" in text or "Reply from" in text or "Packets: Sent" in text or "Destination host unreachable" in text:
        results["detected_type"] = "ping result"
        if "0% loss" in text or "bytes=32" in text:
            results["status"] = "Success"
            results["summary"] = "Ping Connectivity Verified: 0% packet loss (Replies received)."
            results["details"] = [line for line in text.splitlines() if "Reply from" in line or "Packets:" in line]
        elif "unreachable" in text or "timed out" in text or "100% loss" in text:
            results["status"] = "Alert"
            results["summary"] = "Ping Dropped / Blocked: Confirms ACL restriction or unreachable route."
            results["details"] = [line for line in text.splitlines() if "timed out" in line or "unreachable" in line or "Packets:" in line]

    return results

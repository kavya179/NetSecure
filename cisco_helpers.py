"""
NetSecure - Cisco CLI, Subnet Calculator & Dynamic ACL Generator
Provides:
  - Standard IPv4 subnet calculations using python's ipaddress module (arbitrary CIDR /0 to /32)
  - Dynamic Cisco IOS Extended ACL script compilation from user-edited security policies
  - Accurate Cisco CLI command templates reflecting verified Packet Tracer facts
  - CLI terminal output inspector for verification testing
"""

import re
import ipaddress
import pandas as pd

# ---------------------------------------------------------------------------
# 1. ARBITRARY IPv4 SUBNET CALCULATOR (STANDARD ipaddress MODULE)
# ---------------------------------------------------------------------------
def calculate_subnet_details(cidr_input: str) -> dict:
    """
    Computes complete IPv4 subnet details for any valid CIDR prefix (/0 to /32).
    Uses Python's standard library ipaddress module.
    Handles invalid inputs gracefully with clear error messages.
    """
    result = {
        "valid": False,
        "input": cidr_input,
        "network_address": "",
        "broadcast_address": "",
        "netmask": "",
        "wildcard_mask": "",
        "prefixlen": 0,
        "total_addresses": 0,
        "usable_hosts": 0,
        "first_host": "",
        "last_host": "",
        "usable_range": "",
        "ip_type": "",
        "error": None
    }

    if not cidr_input or not str(cidr_input).strip():
        result["error"] = "Subnet input is empty. Please enter an IPv4 network (e.g. 192.168.10.0/24, 10.0.0.0/26, 172.16.1.0/30)."
        return result

    raw_str = str(cidr_input).strip()

    # Append /24 if only an IP without prefix was entered
    if "/" not in raw_str:
        raw_str += "/24"

    try:
        net = ipaddress.ip_network(raw_str, strict=False)
    except ValueError as e:
        result["error"] = f"Invalid IPv4 CIDR notation '{cidr_input}': {str(e)}"
        return result
    except Exception as e:
        result["error"] = f"Error parsing CIDR '{cidr_input}': {str(e)}"
        return result

    result["valid"] = True
    result["network_address"] = str(net.network_address)
    result["netmask"] = str(net.netmask)
    result["wildcard_mask"] = str(net.hostmask)
    result["prefixlen"] = net.prefixlen
    result["total_addresses"] = net.num_addresses
    result["ip_type"] = "Private (RFC 1918)" if net.is_private else "Public Internet"

    if net.prefixlen <= 30:
        result["broadcast_address"] = str(net.broadcast_address)
        result["usable_hosts"] = max(0, net.num_addresses - 2)
        first_ip = net.network_address + 1
        last_ip = net.broadcast_address - 1
        result["first_host"] = str(first_ip)
        result["last_host"] = str(last_ip)
        result["usable_range"] = f"{first_ip} - {last_ip}"
    elif net.prefixlen == 31:
        result["broadcast_address"] = "N/A (RFC 3021 Point-to-Point)"
        result["usable_hosts"] = 2
        result["first_host"] = str(net.network_address)
        result["last_host"] = str(net.broadcast_address)
        result["usable_range"] = f"{net.network_address} - {net.broadcast_address} (Point-to-Point)"
    else:  # /32
        result["broadcast_address"] = "N/A (Single Host IP)"
        result["usable_hosts"] = 1
        result["first_host"] = str(net.network_address)
        result["last_host"] = str(net.network_address)
        result["usable_range"] = f"{net.network_address} (Single Host)"

    return result


# ---------------------------------------------------------------------------
# 2. PROPOSED CISCO EXTENDED ACL COMPILER (ILLUSTRATIVE TEMPLATE GENERATOR)
# ---------------------------------------------------------------------------
def _parse_endpoint_to_cisco_str(raw_val: str, vlans_df: pd.DataFrame = None) -> tuple[str, str]:
    """
    Helper to translate a source/destination description into valid Cisco IOS ACL syntax.
    Safely resolves department names, VLAN IDs, CIDRs, or specific host IPs.
    Returns: (cisco_syntax, error_explanation)
    """
    if not raw_val or not str(raw_val).strip():
        return "any", ""

    val = str(raw_val).strip()
    val_lower = val.lower()

    # Case: Any / All / Internet
    if val_lower in ["any", "all", "internet"]:
        return "any", ""

    # Case: Dynamic resolution from active user-edited vlans_df
    if vlans_df is not None and isinstance(vlans_df, pd.DataFrame) and not vlans_df.empty:
        for _, vrow in vlans_df.iterrows():
            v_name = str(vrow.get("VLAN_Name", "")).strip().lower()
            v_id = str(vrow.get("VLAN_ID", "")).strip()
            v_net = str(vrow.get("Network_Address", "")).strip()
            # Check match against VLAN Name or VLAN ID
            if (v_name and v_name in val_lower) or (v_id and (f"vlan {v_id}" in val_lower or f"vlan{v_id}" in val_lower)):
                try:
                    net = ipaddress.ip_network(v_net, strict=False)
                    return f"{net.network_address} {net.hostmask}", ""
                except ValueError:
                    pass

    # Case: Known department fallback matching Packet Tracer project facts
    if "management" in val_lower or "vlan 10" in val_lower or "vlan10" in val_lower:
        return "192.168.10.0 0.0.0.255", ""
    if "finance" in val_lower or "vlan 20" in val_lower or "vlan20" in val_lower:
        return "192.168.20.0 0.0.0.255", ""
    if ("it" in val_lower and ("vlan" in val_lower or val_lower.strip() == "it")) or "vlan 30" in val_lower or "vlan30" in val_lower:
        return "192.168.30.0 0.0.0.255", ""

    # Case: Look for explicit IP network with CIDR prefix in the string
    match_cidr = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})', val)
    if match_cidr:
        try:
            net = ipaddress.ip_network(match_cidr.group(0), strict=False)
            return f"{net.network_address} {net.hostmask}", ""
        except ValueError as e:
            return "", f"Invalid CIDR in '{val}': {e}"

    # Case: Single Host IP address
    match_ip = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', val)
    if match_ip:
        ip_str = match_ip.group(1)
        try:
            ip = ipaddress.ip_address(ip_str)
            return f"host {ip}", ""
        except ValueError as e:
            return "", f"Invalid IP in '{val}': {e}"

    return "", f"Could not determine valid Cisco network or host syntax from '{val}'"


def generate_cisco_acl_script(security_policies_df: pd.DataFrame, vlans_df: pd.DataFrame = None) -> str:
    """
    Compiles Cisco IOS Extended ACL commands from user-edited security policies
    and VLAN data safely.
    CLEARLY LABELED AS AN ILLUSTRATIVE TEMPLATE: Commands represent proposed policies
    and are NOT automatically pushed to Cisco Packet Tracer.
    """
    lines = [
        "! ===================================================================",
        "! NetSecure: Cisco Catalyst 3650 Extended Access Control List (ACL)",
        "! Proposed Policy Compiler (Illustrative Script Generator)",
        "! ===================================================================",
        "! IMPORTANT NOTICE & DISCLAIMER:",
        "! - This configuration is compiled from the dashboard's active security",
        "!   policy table and VLAN configuration table.",
        "! - Packet Tracer is NOT connected live. These commands are NOT applied",
        "!   automatically to your simulation.",
        "! - To test these policies, copy this script and manually paste it into",
        "!   the CLI of 'Multilayer Switch0' in Cisco Packet Tracer.",
        "! ===================================================================",
        "enable",
        "configure terminal",
        "ip routing",
        ""
    ]

    if security_policies_df is None or len(security_policies_df) == 0:
        lines.append("! No security policies currently defined in dashboard table.")
        return "\n".join(lines)

    lines.append("! -------------------------------------------------------------------")
    lines.append("! Extended Access List: NETSECURE_ENTERPRISE_ACL")
    lines.append("! -------------------------------------------------------------------")
    lines.append("ip access-list extended NETSECURE_ENTERPRISE_ACL")

    rule_count = 0
    for idx, row in security_policies_df.iterrows():
        rule_id = str(row.get("Rule_ID", f"R-{idx+1}")).strip()
        raw_src = str(row.get("Source", "any")).strip()
        raw_dst = str(row.get("Destination", "any")).strip()
        raw_act = str(row.get("Action", "permit")).strip().lower()
        raw_proto = str(row.get("Protocol", "ip")).strip().lower()
        raw_port = str(row.get("Port_Service", "any")).strip().lower()
        purpose = str(row.get("Purpose", "")).strip()

        # Validate action
        action = "deny" if any(w in raw_act for w in ["deny", "block", "drop"]) else "permit"

        # Validate source & destination safely
        src_cisco, src_err = _parse_endpoint_to_cisco_str(raw_src, vlans_df)
        dst_cisco, dst_err = _parse_endpoint_to_cisco_str(raw_dst, vlans_df)

        if src_err or dst_err:
            err_msg = src_err if src_err else dst_err
            lines.append(f" remark [WARNING] Rule {rule_id} skipped: {err_msg}")
            continue

        # Validate protocol
        if "tcp" in raw_proto:
            proto = "tcp"
        elif "udp" in raw_proto:
            proto = "udp"
        elif "icmp" in raw_proto:
            proto = "icmp"
        else:
            proto = "ip"

        # Parse ports if applicable
        port_statements = []
        if proto in ["tcp", "udp"] and raw_port not in ["any", "all", "ip", ""]:
            # Extract port numbers from string (e.g. "80, 443", "53", "22")
            ports_found = re.findall(r'\b\d+\b', raw_port)
            if ports_found:
                for p in ports_found:
                    port_statements.append(f"eq {p}")
            elif "http" in raw_port:
                port_statements.append("eq 80")
            elif "https" in raw_port:
                port_statements.append("eq 443")
            elif "dns" in raw_port:
                port_statements.append("eq 53")
            elif "ssh" in raw_port:
                port_statements.append("eq 22")
            else:
                port_statements.append("")
        else:
            port_statements.append("")

        # Add Remark with purpose
        if purpose:
            lines.append(f" remark --- [{rule_id}] {purpose} ---")

        # Generate command lines
        for port_clause in port_statements:
            cmd = f" {action} {proto} {src_cisco} {dst_cisco}"
            if port_clause:
                cmd += f" {port_clause}"
            if action == "deny" and proto == "ip":
                cmd += " log"
            lines.append(cmd)
            rule_count += 1

    lines.extend([
        " remark --- Default implicit catch-all permit for outbound connectivity ---",
        " permit ip any any",
        "exit",
        "",
        "! -------------------------------------------------------------------",
        "! Inbound Interface Binding Commands (Apply on Multilayer Switch0 SVIs)",
        "! -------------------------------------------------------------------"
    ])

    if vlans_df is not None and isinstance(vlans_df, pd.DataFrame) and not vlans_df.empty:
        for _, vrow in vlans_df.iterrows():
            vid = str(vrow.get("VLAN_ID", "")).strip()
            vname = str(vrow.get("VLAN_Name", "")).strip()
            if vid:
                lines.extend([
                    f"! Apply to VLAN {vid} ({vname} Gateway SVI):",
                    f"interface Vlan{vid}",
                    " ip access-group NETSECURE_ENTERPRISE_ACL in",
                    "exit",
                    ""
                ])
    else:
        lines.extend([
            "! Apply to VLAN 10 (Management Gateway):",
            "interface Vlan10",
            " ip access-group NETSECURE_ENTERPRISE_ACL in",
            "exit",
            "",
            "! Apply to VLAN 20 (finance Gateway):",
            "interface Vlan20",
            " ip access-group NETSECURE_ENTERPRISE_ACL in",
            "exit",
            "",
            "! Apply to VLAN 30 (IT Gateway):",
            "interface Vlan30",
            " ip access-group NETSECURE_ENTERPRISE_ACL in",
            "exit",
            ""
        ])

    lines.extend([
        "end",
        "! Verification CLI Commands:",
        "show access-lists",
        "copy running-config startup-config"
    ])

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 3. VERIFIED CISCO CLI REFERENCES & TEMPLATES
# ---------------------------------------------------------------------------
CISCO_CLI_REFERENCES = {
    "Verified VLAN Configuration": {
        "device": "Multilayer Switch0 & Access Switches (Switch0, 1, 2)",
        "commands": """! Configure Verified Department VLANs
Switch> enable
Switch# configure terminal
Switch(config)# vlan 10
Switch(config-vlan)# name Management
Switch(config-vlan)# exit

Switch(config)# vlan 20
Switch(config-vlan)# name finance
Switch(config-vlan)# exit

Switch(config)# vlan 30
Switch(config-vlan)# name IT
Switch(config-vlan)# exit
Switch(config)# end
Switch# copy running-config startup-config""",
        "verification": "show vlan brief"
    },
    "Verified Access Switch Trunk Link": {
        "device": "Verified Access Switch (Prompt: Switch>)",
        "commands": """! Trunking configuration verified on sample access switch:
Switch> enable
Switch# configure terminal
Switch(config)# interface GigabitEthernet 0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport trunk native vlan 1
Switch(config-if)# switchport trunk allowed vlan 10,20,30
Switch(config-if)# no shutdown
Switch(config-if)# end""",
        "verification": "show interfaces trunk"
    },
    "Verified DHCP Pools Configuration": {
        "device": "Switch (Prompt was Switch> in screenshot; verify on Multilayer Switch0)",
        "commands": """! Verified DHCP Excluded Addresses:
Switch(config)# ip dhcp excluded-address 192.168.10.1
Switch(config)# ip dhcp excluded-address 192.168.20.1
Switch(config)# ip dhcp excluded-address 192.168.30.1

! Verified Pool: Management (VLAN 10)
Switch(config)# ip dhcp pool Management
Switch(dhcp-config)# network 192.168.10.0 255.255.255.0
Switch(dhcp-config)# default-router 192.168.10.1
Switch(dhcp-config)# exit

! Verified Pool: finance (VLAN 20)
Switch(config)# ip dhcp pool finance
Switch(dhcp-config)# network 192.168.20.0 255.255.255.0
Switch(dhcp-config)# default-router 192.168.20.1
Switch(dhcp-config)# dns-server 8.8.8.8
Switch(dhcp-config)# exit

! Verified Pool: IT (VLAN 30)
Switch(config)# ip dhcp pool IT
Switch(dhcp-config)# network 192.168.30.0 255.255.255.0
Switch(dhcp-config)# default-router 192.168.30.1
Switch(dhcp-config)# dns-server 8.8.8.8
Switch(dhcp-config)# exit""",
        "verification": "show ip dhcp binding\nshow ip dhcp pool"
    },
    "Multilayer Switch0 SVIs & Inter-VLAN Routing": {
        "device": "Multilayer Switch0 (Cisco Catalyst 3650 Core)",
        "commands": """! Enable Layer 3 Routing (Unverified on MLS0 until confirmed)
MLS0(config)# ip routing

! SVI for VLAN 10 (Management Gateway)
MLS0(config)# interface Vlan10
MLS0(config-if)# ip address 192.168.10.1 255.255.255.0
MLS0(config-if)# no shutdown
MLS0(config-if)# exit

! SVI for VLAN 20 (finance Gateway)
MLS0(config)# interface Vlan20
MLS0(config-if)# ip address 192.168.20.1 255.255.255.0
MLS0(config-if)# no shutdown
MLS0(config-if)# exit

! SVI for VLAN 30 (IT Gateway)
MLS0(config)# interface Vlan30
MLS0(config-if)# ip address 192.168.30.1 255.255.255.0
MLS0(config-if)# no shutdown
MLS0(config-if)# exit""",
        "verification": "show ip interface brief\nshow ip route"
    }
}

SAMPLE_CLI_OUTPUTS = {
    "PC0 ipconfig & ping 192.168.10.1 (PASS)": """PC>ipconfig

FastEthernet0 Connection:(default port)

   Link-local IPv6 Address.........: FE80::201:64FF:FEA2:4E01
   IP Address......................: 192.168.10.3
   Subnet Mask.....................: 255.255.255.0
   Default Gateway.................: 192.168.10.1

PC>ping 192.168.10.1

Pinging 192.168.10.1 with 32 bytes of data:

Reply from 192.168.10.1: bytes=32 time<1ms TTL=255
Reply from 192.168.10.1: bytes=32 time<1ms TTL=255
Reply from 192.168.10.1: bytes=32 time<1ms TTL=255
Reply from 192.168.10.1: bytes=32 time<1ms TTL=255

Ping statistics for 192.168.10.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms""",

    "PC0 ping 192.168.20.3 (PASS)": """PC>ping 192.168.20.3

Pinging 192.168.20.3 with 32 bytes of data:

Reply from 192.168.20.3: bytes=32 time=1ms TTL=127
Reply from 192.168.20.3: bytes=32 time=1ms TTL=127
Reply from 192.168.20.3: bytes=32 time=1ms TTL=127
Reply from 192.168.20.3: bytes=32 time=1ms TTL=127

Ping statistics for 192.168.20.3:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 1ms, Maximum = 1ms, Average = 1ms""",

    "PC2 Self-Ping (192.168.20.3 Local Stack)": """PC>ping 192.168.20.3

Pinging 192.168.20.3 with 32 bytes of data:

Reply from 192.168.20.3: bytes=32 time<1ms TTL=128
Reply from 192.168.20.3: bytes=32 time<1ms TTL=128
Reply from 192.168.20.3: bytes=32 time<1ms TTL=128
Reply from 192.168.20.3: bytes=32 time<1ms TTL=128

Ping statistics for 192.168.20.3:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms""",

    "show vlan brief (Verified Access Switch)": """VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/4, Fa0/5, Fa0/6, Fa0/7
10   Management                       active    Fa0/1
20   finance                          active    Fa0/2
30   IT                               active    Fa0/3
1002 fddi-default                     active    
1003 token-ring-default               active    
1004 fddinet-default                  active    
1005 trnet-default                    active    """,

    "show interfaces trunk (Verified Access Switch)": """Port        Mode         Encapsulation  Status        Native vlan
Gig0/1      on           802.1q         trunking      1

Port        Vlans allowed on trunk
Gig0/1      10,20,30

Port        Vlans allowed and active in management domain
Gig0/1      10,20,30

Port        Vlans in spanning tree forwarding state and not pruned
Gig0/1      10,20,30"""
}


# ---------------------------------------------------------------------------
# 4. CLI TERMINAL OUTPUT PARSER
# ---------------------------------------------------------------------------
def parse_cisco_output(raw_text: str) -> dict:
    """
    Parses pasted terminal output from Packet Tracer CLI to extract structured evidence.
    """
    results = {
        "detected_type": "Unknown Terminal Output",
        "status": "Neutral",
        "summary": "Could not identify standard Cisco command format.",
        "details": []
    }

    if not raw_text or not raw_text.strip():
        return results

    text = raw_text.strip()

    # Case 1: ipconfig
    if "Link-local IPv6" in text or "IP Address" in text and "Subnet Mask" in text:
        results["detected_type"] = "PC Terminal: ipconfig"
        results["status"] = "Success"
        ips = re.findall(r'IP Address[.\s]+:\s*([0-9.]+)', text)
        gws = re.findall(r'Default Gateway[.\s]+:\s*([0-9.]+)', text)
        ip_str = ips[0] if ips else "Unknown"
        gw_str = gws[0] if gws else "Unknown"
        results["summary"] = f"PC Configuration Detected: IPv4 {ip_str}, Gateway {gw_str}."
        results["details"] = [f"Client IP: {ip_str}", f"Default Gateway: {gw_str}"]

    # Case 2: ping
    elif "Pinging" in text or "Reply from" in text or "Packets: Sent" in text:
        results["detected_type"] = "Ping Connectivity Test"
        if "0% loss" in text or "Lost = 0" in text:
            results["status"] = "Success"
            target_match = re.search(r'Pinging\s+([0-9.]+)', text)
            target = target_match.group(1) if target_match else "Destination"
            results["summary"] = f"Ping to {target} VERIFIED SUCCESSFUL (0% packet loss)."
            results["details"] = [line.strip() for line in text.splitlines() if "Reply from" in line or "Packets:" in line]
        elif "100% loss" in text or "Request timed out" in text or "unreachable" in text:
            results["status"] = "Alert"
            results["summary"] = "Ping DROPPED or UNREACHABLE (Packet loss observed)."
            results["details"] = [line.strip() for line in text.splitlines() if "timed out" in line or "unreachable" in line or "Packets:" in line]

    # Case 3: show vlan brief
    elif "VLAN Name" in text or ("10" in text and "active" in text and "Management" in text):
        results["detected_type"] = "Cisco IOS: show vlan brief"
        vlans_found = []
        for line in text.splitlines():
            m = re.match(r"^(\d+)\s+([A-Za-z0-9_\-]+)\s+(active|act/unsup)", line.strip())
            if m:
                vlans_found.append(f"VLAN {m.group(1)} ({m.group(2)}): Status = {m.group(3)}")
        results["status"] = "Success"
        results["summary"] = f"VLAN Database Detected with {len(vlans_found)} VLAN entries."
        results["details"] = vlans_found

    # Case 4: show interfaces trunk
    elif "Port" in text and ("trunking" in text or "802.1q" in text):
        results["detected_type"] = "Cisco IOS: show interfaces trunk"
        trunks = [line.strip() for line in text.splitlines() if "trunking" in line]
        results["status"] = "Success"
        results["summary"] = f"Detected {len(trunks)} active 802.1Q trunk port(s)."
        results["details"] = trunks

    return results

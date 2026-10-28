# NetSecure: Enterprise Network Design & Security Dashboard

> **College Project:** Computer Networks & Network Security  
> **Topology Tool:** Cisco Packet Tracer (`NetSecure.pkt`)  
> **Dashboard Stack:** Python · Streamlit · Pandas · Matplotlib  
> **GitHub Repository:** [https://github.com/kavya179/NetSecure](https://github.com/kavya179/NetSecure)  

---

## 1. Project Background & Verified Topology

**NetSecure** is an enterprise network design and security monitoring dashboard created to accompany an actual enterprise network designed in **Cisco Packet Tracer**.

### Physical & Logical Topology Devices
- **1 Central Multilayer Switch:** `Multilayer Switch0` (Cisco Catalyst 3650 Core/Distribution switch).
- **3 Access Switches:** `Switch0`, `Switch1`, and `Switch2` (Cisco Catalyst 2960).
- **6 Workstations:** `PC0`, `PC1`, `PC2`, `PC3`, `PC4`, and `PC5`.
- **3 Department Servers:** `Server0`, `Server1`, and `Server2`.

---

## 2. Verified Network Information (From Packet Tracer Screenshots)

The following facts were verified directly from project terminal and configuration evidence:

### A. VLAN Database
| VLAN ID | VLAN Name | Subnet | Gateway | DNS Server | Department Zone |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **10** | `Management` | `192.168.10.0/24` | `192.168.10.1` | Assigned per pool | Purple Section |
| **20** | `finance` | `192.168.20.0/24` | `192.168.20.1` | `8.8.8.8` | Yellow Section |
| **30** | `IT` | `192.168.30.0/24` | `192.168.30.1` | `8.8.8.8` | Pink Section |

### B. Access Switch Interface Sample (Verified on Sample Switch)
- `FastEthernet0/1` → Assigned to **VLAN 10** (`Management`)
- `FastEthernet0/2` → Assigned to **VLAN 20** (`finance`)
- `FastEthernet0/3` → Assigned to **VLAN 30** (`IT`)
- `GigabitEthernet0/1` → **802.1Q Trunk**, Native VLAN 1, VLANs 10, 20, 30 allowed and active.
*(Note: These port assignments were verified on the sample access switch shown in screenshots and are not assumed to apply identically across all switches).*

### C. DHCP Configuration
- **Excluded Addresses:** `192.168.10.1`, `192.168.20.1`, and `192.168.30.1`.
- **Pool `Management`:** Network `192.168.10.0 255.255.255.0`, Default Gateway `192.168.10.1`.
- **Pool `finance`:** Network `192.168.20.0 255.255.255.0`, Default Gateway `192.168.20.1`, DNS `8.8.8.8`.
- **Pool `IT`:** Network `192.168.30.0 255.255.255.0`, Default Gateway `192.168.30.1`, DNS `8.8.8.8`.
*(Commands observed on a device with prompt `Switch>`. Multilayer Switch0 configuration remains to be verified).*

### D. Verified PC Configurations & Confirmed Network Tests
- **`PC0` (Verified via `ipconfig`):**
  - IPv4 Address: `192.168.10.3`
  - Subnet Mask: `255.255.255.0`
  - Default Gateway: `192.168.10.1`
- **`PC2` (Verified via `ipconfig`):**
  - IPv4 Address: `192.168.20.3`
  - Subnet Mask: `255.255.255.0`
  - Default Gateway: `192.168.20.1`

#### Network Connectivity Tests Status:
- **`PC0 → 192.168.10.1` (Default Gateway Ping):** **PASS** (4 packets sent, 4 received, 0% packet loss, RTT <1ms). Confirms local gateway reachability.
- **`PC0 → 192.168.20.3` (Cross-Subnet Reachability Ping):** **PASS** (4 packets sent, 4 received, 0% packet loss). Confirms cross-subnet routing between VLAN 10 (`192.168.10.0/24`) and VLAN 20 (`192.168.20.0/24`). Destination IP matches PC2.
- **All Other Tests (PC2 self-ping, servers, ACLs, switch ports):** **NOT TESTED**. Kept strictly as Not Tested to preserve academic integrity until direct Packet Tracer test output is recorded.

---

## 3. Unverified Items (Pending Direct CLI Confirmation)

To preserve academic integrity and avoid inventing values, the following items are treated as **EXAMPLES / UNVERIFIED**:
1. **Unverified Endpoint IPs:** IP addresses for `PC1`, `PC3`, `PC4`, `PC5`, `Server0`, `Server1`, and `Server2` are unverified; they are marked as examples rather than confirmed values.
2. **Access Switch Port Mappings:** Only sample switch ports (`Fa0/1 -> VLAN 10`, `Fa0/2 -> VLAN 20`, `Fa0/3 -> VLAN 30`, `Gig0/1 -> Trunk`) were observed in CLI; exact port connections across `Switch0`, `Switch1`, and `Switch2` are treated as illustrative models.
3. **Multilayer Switch0 Routing Table:** Direct output of `show ip route` to confirm hardware IP routing and active SVIs.
4. **Server Connectivity & Services:** Ping reachability and web/DNS/database services on Server0, Server1, Server2 remain unverified.
5. **ACL Enforcement:** Empirical verification in CLI that unauthorized cross-department traffic is dropped and logged (ACL generator produces illustrative proposed templates).

---

## 4. Key Dashboard Features & Technical Implementation

- **Strict Evidence Validation Suite:** Prepopulates **ONLY the 2 confirmed tests** (`PC0 → 192.168.10.1` and `PC0 → 192.168.20.3`) as `PASS`. All other 9 checks default to `NOT TESTED`. Test status options are strictly `NOT TESTED`, `PASS`, or `FAIL`.
- **Arbitrary IPv4 Subnet Calculator:** Powered directly by Python's `ipaddress.ip_network(subnet_input, strict=False)`. Correctly calculates network address, broadcast address, subnet netmask, wildcard mask (`net.hostmask`), and usable host range for any CIDR prefix (`/0` to `/32`), including `/24`, `/26`, `/30`, and gracefully handles invalid input with user-friendly error messages.
- **Illustrative Cisco IOS Extended ACL Script Generator:** Compiles Cisco IOS commands from the active editable Security Policy table and VLAN configuration table. Explicitly labeled as an illustrative template for proposed policies that must be manually applied to `Multilayer Switch0` in Packet Tracer.
- **Matplotlib Vector Topology:** Highlights confirmed links and verified devices (`PC0: 192.168.10.3`, `PC2: 192.168.20.3`) in Green, while marking unverified connections and example ports with dotted illustrative styling.
- **Live Terminal Output Inspector:** Paste CLI output from `ipconfig`, `ping`, `show vlan brief`, or `show interfaces trunk` to extract validation proof.
- **No Fabricated Telemetry:** Displays an explicit simulation notice: *"Packet Tracer simulation is not connected directly. Results are recorded manually from real CLI outputs."*

---

## 5. Installation and Execution (Windows & VS Code)

### Prerequisites
- Python 3.10 or higher.
- VS Code or Windows PowerShell.

### Step 1: Open Terminal in Project Directory
```powershell
cd c:\Users\DELL\Desktop\Sem_5\NetSecure
```

### Step 2: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Streamlit Dashboard
Execute the exact command:
```powershell
python -m streamlit run app.py
```

### Step 4: Access the Dashboard
Navigate in any web browser to:
```
http://localhost:8501
```

---

## 6. Project Defense / Viva Questions & Answers

1. **Why does PC0 have IP 192.168.10.3 instead of 192.168.10.2?**
   - *Answer:* The DHCP configuration excluded `192.168.10.1` (the default gateway). Depending on lease sequence or switch management addressing (`192.168.10.2` often reserved for switch SVI management), PC0 received `.3` from the pool.

2. **Does PC0 pinging 192.168.20.3 prove Inter-VLAN routing is active?**
   - *Answer:* Yes! PC0 resides in subnet `192.168.10.0/24` (VLAN 10), while destination `192.168.20.3` is in subnet `192.168.20.0/24` (VLAN 20). Successfully pinging between two different subnets confirms that a Layer 3 routing entity (the default gateway on the Multilayer Switch) forwarded the packets between VLANs.

3. **Why is PC2 pinging 192.168.20.3 considered a self-ping and not an inter-VLAN test?**
   - *Answer:* Because `192.168.20.3` is PC2's own IP address. A host pinging its own interface tests its local TCP/IP protocol stack and NIC driver; it does not generate outbound network traffic across the switch trunk or default gateway.

4. **Why are trunk links between the Multilayer Switch and access switches necessary?**
   - *Answer:* Trunk links use IEEE 802.1Q encapsulation to multiplex frames from multiple VLANs (10, 20, 30) across a single physical cable by inserting a 4-byte tag containing the VLAN ID.

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

### D. Verified PC Configurations & Connectivity Tests
- **`PC0` (Verified via `ipconfig`):**
  - IPv4 Address: `192.168.10.3`
  - Subnet Mask: `255.255.255.0`
  - Default Gateway: `192.168.10.1`
- **`PC0 → 192.168.10.1` (Gateway Ping):** **PASS** (4 packets sent, 4 received, 0% loss, RTT <1ms).
- **`PC0 → 192.168.20.3` (Inter-Subnet Reachability):** **PASS** (4 packets sent, 4 received, 0% loss). Demonstrates reachability across subnets to `192.168.20.0/24`. Destination is believed to be PC2 based on displayed PC2 info.
- **`PC2` (Verified via `ipconfig`):**
  - IPv4 Address: `192.168.20.3`.
  - Self-ping test (`ping 192.168.20.3` from PC2): 4/4 packets received on second attempt. Verified local stack loopback (not an inter-VLAN test).

---

## 3. What Still Requires Verification in Packet Tracer

To preserve academic integrity, the following items are displayed as **UNVERIFIED / PENDING EVIDENCE**:
1. **Central Multilayer Switch Routing:** Output of `show ip route` to confirm hardware IP routing and active SVIs.
2. **Remaining Host IPs:** IP addresses for `PC1`, `PC3`, `PC4`, `PC5`, `Server0`, `Server1`, and `Server2`.
3. **Switch Interface Assignments:** Port mappings on `Switch1` and `Switch2`.
4. **Server Connectivity & Services:** Ping reachability and web/DNS/database services on Server0, 1, 2.
5. **ACL Enforcement:** Empirical verification in CLI that unauthorized cross-department traffic is dropped and logged.

---

## 4. Key Dashboard Features & Bug Fixes

- **No Fabricated Telemetry:** Displays an explicit simulation notice: *"Packet Tracer simulation is not connected directly. Results are recorded manually from real CLI outputs."*
- **Arbitrary IPv4 Subnet Calculator:** Uses Python's standard `ipaddress` module to calculate network base, broadcast address, netmask, wildcard hostmask, usable host range, and address scope for any valid CIDR prefix (`/0` to `/32`), such as `/24`, `/26`, `/30`, `/16`. Includes graceful error validation.
- **Dynamic Cisco IOS Extended ACL Compiler:** Generates Cisco IOS commands dynamically from active rows in the editable security policy table, rather than static hardcoded text.
- **Matplotlib Vector Topology:** Highlights confirmed links and verified devices (`PC0: 192.168.10.3`, `PC2: 192.168.20.3`) in Green, while marking unverified connections as illustrative models.
- **Strict Evidence Validation Suite:** Prepopulates only confirmed tests as `PASS`. All other checks default to `NOT TESTED`. Test status options are strictly `NOT TESTED`, `PASS`, or `FAIL`.
- **Live Terminal Output Inspector:** Paste CLI output from `ipconfig`, `ping`, `show vlan brief`, or `show interfaces trunk` to extract validation proof.

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

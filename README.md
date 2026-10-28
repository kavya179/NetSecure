# NetSecure: Enterprise Network Design & Security Dashboard

> **College Project:** Computer Networks & Network Security  
> **Topology Tool:** Cisco Packet Tracer  
> **Dashboard Stack:** Python · Streamlit · Pandas · Matplotlib  

---

## 1. Project Background

**NetSecure** is an enterprise-grade network design and security monitoring dashboard developed as a companion to an enterprise network simulated in **Cisco Packet Tracer**. 

The network architecture implements a hierarchical **3-tier campus distribution and access model**:

- **1 Cisco Catalyst 3650 Multilayer Switch (`Multilayer Switch0`)**: Serves as the distribution and core routing engine. Handles wire-speed Inter-VLAN routing via Switch Virtual Interfaces (SVIs), centralized DHCP pools, and Extended Access Control Lists (ACLs).
- **3 Cisco Catalyst 2960 Access Switches (`Switch0`, `Switch1`, `Switch2`)**: Provide Layer 2 access connectivity to departmental endpoints and link to the core via IEEE 802.1Q trunk links.
- **6 Workstations (`PC0` to `PC5`)**: Two PCs assigned per department.
- **3 Department Servers (`Server0`, `Server1`, `Server2`)**: One dedicated server per department providing localized services (DNS/Web, HR Portal, Accounting Database).
- **3 Isolated Departmental Segments (VLANs 10, 20, 30)**:
  - **Purple Section (VLAN 10):** IT & Engineering (`Switch0`, `PC0`, `PC1`, `Server0`)
  - **Yellow Section (VLAN 20):** Human Resources & Administration (`Switch1`, `PC2`, `PC3`, `Server1`)
  - **Pink Section (VLAN 30):** Finance & Accounting (`Switch2`, `PC4`, `PC5`, `Server2`)

---

## 2. Dashboard Design & Aesthetic

The dashboard features a **dark navy Network Operations Center (NOC) aesthetic**:
- **Palette:** Dark navy base (`#0B1120`, `#0F172A`), cyan (`#06B6D4`) and sky blue (`#38BDF8`) accents.
- **Status Coding:** Green for verified successful tests, Yellow for unverified / warnings, Red for failed tests.
- **Visual Department Matching:** Purple, Yellow, and Pink borders and badges mirroring the Packet Tracer visual layout.
- **High Readability:** Responsive card grids, interactive data tables, copyable Cisco CLI snippets, and high-DPI vector topology diagrams.

---

## 3. Required Pages & Capabilities

### Page 1: Overview & System Health
- High-level executive narrative of the network topology.
- Real-time KPI metric cards: Departments (3), Switches (4), Endpoints (9), Active VLANs (3).
- Verification progress bar and test outcome distribution (Passed, Untested, Failed).
- Departmental visual zone breakdown with assigned devices and default subnets.

### Page 2: Network Topology
- High-resolution dynamic diagram rendered via **Matplotlib**:
  - Core Multilayer Switch at top with SVI gateway IPs.
  - IEEE 802.1Q Trunk links labeled with interfaces (`Gig1/0/1`, `Gig1/0/2`, `Gig1/0/3`).
  - Access switches in middle layer (`Switch0`, `Switch1`, `Switch2`).
  - End-user workstations and servers grouped into their respective Purple, Yellow, and Pink zones.
- Complete device inventory and interface mapping table.
- CSV export for hardware inventory.

### Page 3: VLAN and IP Addressing Plan
- Interactive editable tables using `st.data_editor`:
  - **Departmental VLAN Table:** Edit VLAN IDs, Network Addresses, Subnet Masks, Gateways, and Statuses.
  - **Endpoint Device Matrix:** Detailed mapping of PC0-PC5 and Server0-Server2 with IP, port assignments, and gateway.
- Subnet Address Range Calculator (computes network base, broadcast address, and usable IP range).
- One-click CSV export for both VLAN and endpoint allocation tables.
- Clearly labeled example data notice (academic integrity).

### Page 4: Security Policy & Cisco IOS ACL Compiler
- Security access control matrix defining source, destination, action (Permit/Deny), protocol, purpose, and verification status.
- **Cisco IOS Extended ACL Compiler:** Automatically generates copy-pasteable Cisco Catalyst 3650 configuration commands:
  - Department isolation (blocking HR from Finance records).
  - Controlled server access (HTTP/HTTPS to HR Portal, SQL/HTTPS to Finance DB).
  - IT administrative override and network DNS resolution.
  - SVI inbound access-group bindings.
- Downloadable `.txt` Cisco configuration script and CSV policy export.

### Page 5: Validation Suite & Test Logs
- Comprehensive verification checklist covering:
  - `show vlan brief` (VLAN database)
  - `show interfaces trunk` (802.1Q trunk links)
  - `show ip interface brief` (SVI gateway interfaces)
  - `show ip route` (Inter-VLAN routing table)
  - `show ip dhcp binding` (DHCP address allocation)
  - Intra-VLAN and Inter-VLAN `ping` tests
  - ACL permit/deny verification
  - `show port-security` (Layer 2 port security)
- **Zero Auto-Pass Policy:** Tests must be verified in Packet Tracer before recording as Passed or Failed.
- Interactive status recorder with timestamp and notes logging.
- **Cisco CLI Output Inspector:** Paste terminal text to parse and extract verification proof.
- **Cisco Commands Reference Guide:** Complete cheatsheet of configuration commands.
- One-click CSV export of test logs.

---

## 4. Cisco Packet Tracer Integration Architecture

- **Proprietary File Architecture:** Cisco Packet Tracer stores network states in proprietary binary `.pkt` files. There is no open-source Python library that can parse or modify `.pkt` binary formats natively without the desktop application running.
- **External IPC Constraints:** Packet Tracer communicates externally only when configured with its Multi-User / PT-IPC socket listener.
- **Companion Mode Design:** To maintain 100% reliability during college project demonstrations, the dashboard runs in **Manual Companion Mode**. Students execute commands directly in Packet Tracer's CLI, observe results, and record verified proof in the dashboard.
- **Modular Extensibility:** All data structures are separated into `data_manager.py` and `cisco_helpers.py`, allowing future REST or socket API modules to plug in seamlessly.

---

## 5. Installation and Execution (Windows & VS Code)

### Prerequisites
- Python 3.10 or higher installed on Windows.
- VS Code (or PowerShell terminal).

### Step 1: Open Terminal in Project Directory
Open VS Code, press `Ctrl + ~` to open the integrated terminal, and ensure your terminal is in the project folder:
```powershell
cd c:\Users\DELL\Desktop\Sem_5
```

### Step 2: (Optional but Recommended) Create a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If you see an ExecutionPolicy error in PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Streamlit Dashboard
Execute the exact command:
```powershell
python -m streamlit run app.py
```

### Step 5: Access the Dashboard
Streamlit will automatically open your default browser. If it doesn't open automatically, navigate to:
```
http://localhost:8501
```

---

## 6. Troubleshooting Common Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `streamlit: command not found` | Streamlit not in PATH or wrong environment | Run using `python -m streamlit run app.py` |
| `Port 8501 already in use` | A previous instance is still running | Run on a different port: `python -m streamlit run app.py --server.port 8502` |
| `ExecutionPolicy error in PowerShell` | Windows script execution restricted | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| Missing packages error | Dependencies not yet installed | Run `pip install -r requirements.txt` |

---

## 7. College Viva & Project Defense Guide

During your project viva or demo, be prepared to answer these core networking questions:

1. **Why use a Multilayer Switch (Catalyst 3650) instead of a Router-on-a-Stick?**
   - *Answer:* A Multilayer Switch performs Inter-VLAN routing in hardware at wire speed using Application-Specific Integrated Circuits (ASICs), avoiding the single-link bandwidth bottleneck of a traditional router-on-a-stick topology.

2. **What is an SVI (Switch Virtual Interface)?**
   - *Answer:* An SVI is a Layer 3 logical interface associated with a specific VLAN (e.g., `interface Vlan10`). It holds an IP address that functions as the default gateway for all endpoints in that VLAN.

3. **How does 802.1Q trunking work between the switches?**
   - *Answer:* 802.1Q inserts a 4-byte VLAN tag into standard Ethernet frames across trunk links, allowing multiple VLANs (10, 20, 30) to share a single physical uplink without leaking traffic between departments.

4. **Where should Extended Access Control Lists (ACLs) be applied?**
   - *Answer:* In Cisco network design best practices, Extended ACLs should be applied as close to the traffic source as possible (inbound on the source SVI interface) to drop unauthorized packets before they consume backbone switching capacity.

---

## 8. License & Academic Attribution
Developed for educational demonstration in Computer Networks and Network Security courses. Free to adapt and customize for academic presentations.

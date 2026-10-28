"""
NetSecure - Dynamic Network Topology Generator
Generates a professional Matplotlib topology visualization matching the Cisco Packet Tracer layout.
Accurately reflects verified facts:
  - Multilayer Switch0 (Cisco Catalyst 3650 Core/Distribution)
  - Access Switches: Switch0, Switch1, Switch2
  - Purple Section: Management (VLAN 10) · PC0 (192.168.10.3 VERIFIED), PC1, Server0
  - Yellow Section: finance (VLAN 20) · PC2 (192.168.20.3 VERIFIED), PC3, Server1
  - Pink Section: IT (VLAN 30) · PC4, PC5, Server2
  - Confirmed vs. illustrative links clearly indicated
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def render_topology_diagram():
    """
    Renders and returns a high-resolution Matplotlib Figure representing the
    Cisco Packet Tracer Enterprise Network Topology.
    Clearly distinguishes verified links and devices from illustrative models.
    """
    fig, ax = plt.subplots(figsize=(14.2, 9.2), facecolor='#0B1120')
    ax.set_facecolor('#0B1120')

    # Coordinates setup
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-1.2, 10.4)
    ax.axis('off')

    # Color definitions matching Packet Tracer visual departments
    cyan_accent = '#06B6D4'
    blue_accent = '#38BDF8'
    text_white = '#F8FAFC'
    text_muted = '#94A3B8'
    green_verified = '#10B981'

    dept_styles = {
        'Purple': {
            'x_min': 0.2, 'x_max': 4.4, 'y_min': 0.1, 'y_max': 6.6,
            'color': '#A855F7', 'bg': '#190E2D', 'border': '#9333EA',
            'title': 'PURPLE ZONE · MANAGEMENT',
            'vlan': 'VLAN 10 · 192.168.10.0/24 · GW: 192.168.10.1',
            'switch_x': 2.3, 'switch_y': 5.2,
            'pc0_x': 1.1, 'pc0_y': 2.3,
            'pc1_x': 2.3, 'pc1_y': 2.3,
            'server_x': 3.5, 'server_y': 2.3
        },
        'Yellow': {
            'x_min': 4.8, 'x_max': 9.2, 'y_min': 0.1, 'y_max': 6.6,
            'color': '#EAB308', 'bg': '#261D04', 'border': '#CA8A04',
            'title': 'YELLOW ZONE · FINANCE',
            'vlan': 'VLAN 20 · 192.168.20.0/24 · GW: 192.168.20.1 · DNS: 8.8.8.8',
            'switch_x': 7.0, 'switch_y': 5.2,
            'pc0_x': 5.8, 'pc0_y': 2.3,
            'pc1_x': 7.0, 'pc1_y': 2.3,
            'server_x': 8.2, 'server_y': 2.3
        },
        'Pink': {
            'x_min': 9.6, 'x_max': 13.8, 'y_min': 0.1, 'y_max': 6.6,
            'color': '#EC4899', 'bg': '#2C0920', 'border': '#DB2777',
            'title': 'PINK ZONE · IT',
            'vlan': 'VLAN 30 · 192.168.30.0/24 · GW: 192.168.30.1 · DNS: 8.8.8.8',
            'switch_x': 11.7, 'switch_y': 5.2,
            'pc0_x': 10.5, 'pc0_y': 2.3,
            'pc1_x': 11.7, 'pc1_y': 2.3,
            'server_x': 12.9, 'server_y': 2.3
        }
    }

    # Top Title & Simulation Banner
    ax.text(7.0, 10.05, "NETSECURE ENTERPRISE NETWORK TOPOLOGY",
            ha='center', va='center', fontsize=13, fontweight='bold',
            color=text_white, fontfamily='sans-serif')
    ax.text(7.0, 9.75, "Cisco Packet Tracer Logical Topology · 3-Tier Campus Distribution & Access Model",
            ha='center', va='center', fontsize=9.0, color=cyan_accent, fontfamily='sans-serif')
    ax.text(7.0, 9.45, "NOT CONNECTED LIVE: Manual representation based on verified Packet Tracer screenshots",
            ha='center', va='center', fontsize=7.5, color='#F59E0B', fontfamily='sans-serif')

    # Draw Department Zone Backdrops
    for key, d in dept_styles.items():
        rect = patches.FancyBboxPatch(
            (d['x_min'], d['y_min']), d['x_max'] - d['x_min'], d['y_max'] - d['y_min'],
            boxstyle="round,pad=0.25,rounding_size=0.4",
            facecolor=d['bg'], edgecolor=d['border'],
            linewidth=1.8, linestyle='-', alpha=0.9, zorder=1
        )
        ax.add_patch(rect)

        # Department Header Tag
        tag_box = patches.FancyBboxPatch(
            (d['x_min'] + 0.12, d['y_max'] - 0.58), (d['x_max'] - d['x_min']) - 0.24, 0.48,
            boxstyle="round,pad=0.1,rounding_size=0.2",
            facecolor='#0B1120', edgecolor=d['border'],
            linewidth=1.2, zorder=2
        )
        ax.add_patch(tag_box)
        ax.text((d['x_min'] + d['x_max']) / 2, d['y_max'] - 0.24, d['title'],
                ha='center', va='center', fontsize=8.2, fontweight='bold', color=d['color'], zorder=3)
        ax.text((d['x_min'] + d['x_max']) / 2, d['y_max'] - 0.45, d['vlan'],
                ha='center', va='center', fontsize=6.8, color=text_muted, zorder=3)

    # Core Multilayer Switch Coordinates
    mls_x, mls_y = 7.0, 8.3

    # Trunk Links: Multilayer Switch0 to each Access Switch
    trunk_targets = [
        (dept_styles['Purple']['switch_x'], dept_styles['Purple']['switch_y'], "Uplink to Switch0", True),
        (dept_styles['Yellow']['switch_x'], dept_styles['Yellow']['switch_y'], "Uplink to Switch1", False),
        (dept_styles['Pink']['switch_x'], dept_styles['Pink']['switch_y'], "Uplink to Switch2", False)
    ]

    for tx, ty, label_text, is_verified_port in trunk_targets:
        # Glow link
        ax.plot([mls_x, tx], [mls_y - 0.4, ty + 0.4], color='#0284C7', linewidth=4.0, alpha=0.25, zorder=4)
        # Main link line
        ax.plot([mls_x, tx], [mls_y - 0.4, ty + 0.4], color='#38BDF8', linewidth=2.0, linestyle='--', zorder=5)
        # Trunk Label
        mid_x = (mls_x + tx) / 2
        mid_y = (mls_y - 0.4 + ty + 0.4) / 2 + 0.18
        rot = 18 if tx < mls_x else (-18 if tx > mls_x else 0)
        trunk_tag = "Gig0/1 · 802.1Q TRUNK [VERIFIED]" if is_verified_port else "802.1Q TRUNK [ILLUSTRATIVE]"
        ax.text(mid_x, mid_y, trunk_tag, ha='center', va='center',
                fontsize=6.5, fontweight='bold', color='#38BDF8' if not is_verified_port else green_verified,
                rotation=rot,
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#0B1120', edgecolor='#0284C7', alpha=0.9),
                zorder=6)

    # Core Multilayer Switch (Catalyst 3650)
    core_box = patches.FancyBboxPatch(
        (mls_x - 1.95, mls_y - 0.52), 3.9, 0.98,
        boxstyle="round,pad=0.15,rounding_size=0.3",
        facecolor='#1E293B', edgecolor='#38BDF8',
        linewidth=2.2, zorder=10
    )
    ax.add_patch(core_box)
    
    # Layer 3 Badge
    l3_badge = patches.FancyBboxPatch(
        (mls_x - 0.9, mls_y + 0.28), 1.8, 0.24,
        boxstyle="round,pad=0.05,rounding_size=0.1",
        facecolor='#0369A1', edgecolor='#38BDF8',
        linewidth=0.8, zorder=11
    )
    ax.add_patch(l3_badge)
    ax.text(mls_x, mls_y + 0.4, "LAYER 3 MULTILAYER SWITCH", ha='center', va='center',
            fontsize=6.5, fontweight='bold', color='#FFFFFF', zorder=12)

    ax.text(mls_x, mls_y + 0.12, "Multilayer Switch0", ha='center', va='center',
            fontsize=11.5, fontweight='bold', color='#FFFFFF', zorder=11)
    ax.text(mls_x, mls_y - 0.12, "Cisco Catalyst 3650 · Inter-VLAN Routing & ACL Engine", ha='center', va='center',
            fontsize=7.8, color='#38BDF8', zorder=11)
    ax.text(mls_x, mls_y - 0.34, "Gateways: Vlan10 (192.168.10.1) · Vlan20 (192.168.20.1) · Vlan30 (192.168.30.1)",
            ha='center', va='center', fontsize=6.8, color=text_muted, zorder=11)

    # Department Device Inventory mapping
    dept_devices = [
        ('Purple', 'Switch0', 'PC0', 'PC1', 'Server0', 'Fa0/1', 'Unconfirmed', 'Unconfirmed'),
        ('Yellow', 'Switch1', 'PC2', 'PC3', 'Server1', 'Fa0/2', 'Unconfirmed', 'Unconfirmed'),
        ('Pink', 'Switch2', 'PC4', 'PC5', 'Server2', 'Fa0/3', 'Unconfirmed', 'Unconfirmed')
    ]

    for color_key, sw_name, pc_a_name, pc_b_name, srv_name, p_a, p_b, p_srv in dept_devices:
        cfg = dept_styles[color_key]
        sx, sy = cfg['switch_x'], cfg['switch_y']

        # Access Switch Card
        sw_box = patches.FancyBboxPatch(
            (sx - 1.25, sy - 0.45), 2.5, 0.85,
            boxstyle="round,pad=0.15,rounding_size=0.25",
            facecolor='#131F37', edgecolor=cfg['color'],
            linewidth=1.8, zorder=10
        )
        ax.add_patch(sw_box)

        # L2 Badge
        l2_badge = patches.FancyBboxPatch(
            (sx - 0.65, sy + 0.28), 1.3, 0.2,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor='#1E293B', edgecolor=cfg['color'],
            linewidth=0.7, zorder=11
        )
        ax.add_patch(l2_badge)
        ax.text(sx, sy + 0.38, "ACCESS SWITCH", ha='center', va='center',
                fontsize=5.8, fontweight='bold', color=cfg['color'], zorder=12)

        ax.text(sx, sy + 0.1, sw_name, ha='center', va='center',
                fontsize=10.0, fontweight='bold', color=text_white, zorder=11)
        ax.text(sx, sy - 0.12, "Cisco Catalyst 2960", ha='center', va='center',
                fontsize=7.4, color=cfg['color'], zorder=11)
        ax.text(sx, sy - 0.30, "Uplink to MLS0 (Gig0/1)", ha='center', va='center',
                fontsize=6.5, color=text_muted, zorder=11)

        # Draw Links to PCs and Server
        endpoints = [
            (cfg['pc0_x'], cfg['pc0_y'], pc_a_name, "WORKSTATION", p_a,
             "192.168.10.3" if pc_a_name == "PC0" else ("192.168.20.3" if pc_a_name == "PC2" else "Unverified"),
             True if pc_a_name in ["PC0", "PC2"] else False),
            (cfg['pc1_x'], cfg['pc1_y'], pc_b_name, "WORKSTATION", p_b, "Unverified", False),
            (cfg['server_x'], cfg['server_y'], srv_name, "SERVER", p_srv, "Unverified", False)
        ]

        for ep_x, ep_y, name, dev_type, port_lbl, host_ip, is_verified in endpoints:
            is_server = (dev_type == "SERVER")
            
            # Access link line: Solid if port is verified, dashed if illustrative
            line_style = '-' if is_verified else ':'
            line_alpha = 0.8 if is_verified else 0.45
            ax.plot([sx, ep_x], [sy - 0.45, ep_y + 0.55],
                    color=green_verified if is_verified else cfg['border'],
                    linewidth=1.6 if is_verified else 1.2,
                    linestyle=line_style, alpha=line_alpha, zorder=5)

            # Port label on link
            link_mid_x = (sx + ep_x) / 2
            link_mid_y = (sy - 0.45 + ep_y + 0.55) / 2
            ax.text(link_mid_x, link_mid_y, port_lbl, ha='center', va='center',
                    fontsize=5.8, color=green_verified if is_verified else text_muted,
                    bbox=dict(boxstyle='square,pad=0.1', facecolor='#0B1120', edgecolor='none', alpha=0.85),
                    zorder=6)

            # Endpoint Box
            box_width = 1.05
            box_height = 1.10

            ep_box = patches.FancyBboxPatch(
                (ep_x - box_width/2, ep_y - box_height/2), box_width, box_height,
                boxstyle="round,pad=0.12,rounding_size=0.2",
                facecolor='#111C30' if not is_server else '#16233B',
                edgecolor=green_verified if is_verified else (cfg['color'] if is_server else '#334155'),
                linewidth=1.8 if is_verified else (1.4 if is_server else 1.0),
                linestyle='--' if is_server else '-',
                zorder=10
            )
            ax.add_patch(ep_box)

            # Tag badge inside endpoint box
            tag_color = green_verified if is_verified else (cfg['color'] if is_server else '#38BDF8')
            type_tag = "[ SRV ]" if is_server else "[ HOST ]"
            ax.text(ep_x, ep_y + 0.35, type_tag, ha='center', va='center',
                    fontsize=6.0, fontweight='bold', color=tag_color, zorder=11)
            ax.text(ep_x, ep_y + 0.10, name, ha='center', va='center',
                    fontsize=9.0, fontweight='bold', color=text_white, zorder=11)
            
            # IP Label & Verification tag
            if is_verified:
                ax.text(ep_x, ep_y - 0.12, host_ip, ha='center', va='center',
                        fontsize=6.8, fontweight='bold', color=green_verified, zorder=11)
                ax.text(ep_x, ep_y - 0.33, "[VERIFIED]", ha='center', va='center',
                        fontsize=5.8, fontweight='bold', color=green_verified, zorder=11)
            else:
                ax.text(ep_x, ep_y - 0.12, f"VLAN {cfg['vlan'].split()[1]}", ha='center', va='center',
                        fontsize=6.2, color=cfg['color'], zorder=11)
                ax.text(ep_x, ep_y - 0.33, "[UNVERIFIED IP]", ha='center', va='center',
                        fontsize=5.5, color='#F59E0B', zorder=11)

    # Bottom Legend Banner
    legend_box = patches.FancyBboxPatch(
        (0.2, -1.05), 13.6, 0.95,
        boxstyle="round,pad=0.1,rounding_size=0.2",
        facecolor='#0F172A', edgecolor='#1E293B',
        linewidth=1.0, zorder=15
    )
    ax.add_patch(legend_box)

    # Legend text items
    ax.text(0.5, -0.45, "TOPOLOGY LEGEND & EVIDENCE KEY:", fontsize=7.6, fontweight='bold', color='#38BDF8', zorder=16)
    ax.text(4.2, -0.45, "[VERIFIED] Tested in Packet Tracer", fontsize=7.2, color=green_verified, fontweight='bold', zorder=16)
    ax.text(8.2, -0.45, "[UNVERIFIED] Illustrative model; requires CLI evidence", fontsize=7.2, color='#F59E0B', zorder=16)
    
    ax.text(0.5, -0.80, "■ Cisco 3650 Core MLS", fontsize=6.8, color=text_white, zorder=16)
    ax.text(2.6, -0.80, "■ Cisco 2960 Access Switch", fontsize=6.8, color=text_white, zorder=16)
    ax.text(5.0, -0.80, "― Solid Line: Confirmed Trunk / Port (Gig0/1, Fa0/1-3 on sample switch)", fontsize=6.8, color=green_verified, zorder=16)
    ax.text(10.2, -0.80, "··· Dotted Line: Illustrative Link", fontsize=6.8, color=text_muted, zorder=16)

    plt.tight_layout()
    return fig

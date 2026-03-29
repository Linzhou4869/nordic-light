#!/usr/bin/env python3
"""Generate VIX Breach Architecture Diagram using Matplotlib"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, ConnectionPatch
import numpy as np

def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(16, 20), facecolor='white')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(50, 98, 'VIX BREACH EXECUTION FLOW ARCHITECTURE', 
            fontsize=18, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='none', pad=0.5))
    
    ax.text(50, 95, f'VIX: 31.05 | Threshold: 18.00 | Status: ⚠️ BREACH DETECTED | 2026-03-29 11:19 GMT+8',
            fontsize=11, ha='center', va='top', color='#c62828', fontweight='bold')
    
    # Node definitions: (x, y, width, height, label, color, fontsize=10)
    nodes = [
        # Data Layer
        (40, 88, 20, 4, '📊 CBOE Data Feed', '#e3f2fd', 11),
        (40, 80, 20, 5, 'Threshold Check\n(VIX > 18?)', '#fff9c4', 10),
        
        # Status
        (25, 70, 20, 4, '🚨 BREACH\nTRIGGERED', '#ffcdd2', 10),
        (55, 70, 20, 4, '✅ Normal\nOperations', '#c8e6c9', 10),
        
        # Alert System
        (25, 60, 20, 3, '🔔 Alert System', '#ffe0b2', 10),
        (10, 53, 15, 3, 'Silence Audio', '#ffcc80', 9),
        (25, 53, 15, 3, 'Log Event', '#ffe0b2', 9),
        (40, 53, 15, 3, 'Notify', '#ffe0b2', 9),
        
        # Execution Engine
        (25, 43, 20, 4, '⚙️ Execution Engine', '#e1bee7', 11),
        
        # Three Branches
        (10, 33, 18, 3, 'Hedge Positions', '#f8bbd9', 10),
        (25, 33, 18, 3, 'Risk Rebalancing', '#f8bbd9', 10),
        (40, 33, 18, 3, 'Liquidity Check', '#f8bbd9', 10),
        
        # Hedge Actions
        (5, 25, 10, 2.5, 'VIX Futures', '#f48fb1', 8),
        (15, 25, 10, 2.5, 'SPX Puts', '#f48fb1', 8),
        (25, 25, 10, 2.5, 'Treasury', '#f48fb1', 8),
        
        # Rebalancing Actions
        (35, 25, 10, 2.5, 'Reduce Equity', '#f48fb1', 8),
        (45, 25, 10, 2.5, 'Increase Cash', '#f48fb1', 8),
        (55, 25, 10, 2.5, 'Tail Hedges', '#f48fb1', 8),
        
        # Liquidity Actions
        (15, 17, 10, 2.5, 'Counterparty', '#f48fb1', 8),
        (25, 17, 10, 2.5, 'Margin Check', '#f48fb1', 8),
        (35, 17, 10, 2.5, 'Settlement', '#f48fb1', 8),
        
        # Confirmation
        (40, 9, 20, 3, '📝 Trade Confirmation', '#b3e5fc', 10),
        
        # Reporting
        (15, 3, 12, 2.5, '📤 Post to X', '#1da1f2', 9),
        (40, 3, 12, 2.5, '📁 Archive', '#b3e5fc', 9),
        (65, 3, 12, 2.5, '🔐 Audit Log', '#b3e5fc', 9),
        
        # Complete
        (40, -3, 20, 4, '✅ Execution Complete', '#a5d6a7', 11),
    ]
    
    # Draw nodes
    node_centers = []
    for i, (x, y, w, h, label, color, fs) in enumerate(nodes):
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='#333', 
                                  facecolor=color, zorder=10)
        ax.add_patch(rect)
        node_centers.append((x + w/2, y + h/2))
        
        # Text
        lines = label.split('\n')
        for j, line in enumerate(lines):
            ax.text(x + w/2, y + h/2 + (len(lines)-1)/2 - j*0.9, line,
                   fontsize=fs, ha='center', va='center', fontweight='bold' if 'BREACH' in label else 'normal')
    
    # Draw arrows (simplified - vertical flow)
    arrow_style = "arrowstyle=->,connectionstyle=arc3,rad=0.1"
    
    # Main flow arrows
    arrows = [
        (0, 1),   # CBOE -> Threshold
        (1, 2),   # Threshold -> Breach
        (1, 3),   # Threshold -> Normal
        (2, 4),   # Breach -> Alert
        (4, 5),   # Alert -> Silence
        (4, 6),   # Alert -> Log
        (4, 7),   # Alert -> Notify
        (2, 8),   # Breach -> Execution
        (8, 9),   # Execution -> Hedge
        (8, 10),  # Execution -> Rebalance
        (8, 11),  # Execution -> Liquidity
        (9, 12),  # Hedge -> VIX Futures
        (9, 13),  # Hedge -> SPX Puts
        (9, 14),  # Hedge -> Treasury
        (10, 15), # Rebalance -> Reduce Equity
        (10, 16), # Rebalance -> Increase Cash
        (10, 17), # Rebalance -> Tail Hedges
        (11, 18), # Liquidity -> Counterparty
        (11, 19), # Liquidity -> Margin
        (11, 20), # Liquidity -> Settlement
    ]
    
    for src, dst in arrows:
        if src < len(node_centers) and dst < len(node_centers):
            xy1 = node_centers[src]
            xy2 = node_centers[dst]
            arrow = FancyArrowPatch(xy1, xy2, arrowstyle='->', 
                                    connectionstyle='arc3,rad=0.1',
                                    color='#555', linewidth=1.5, zorder=5)
            ax.add_patch(arrow)
    
    # Arrows to confirmation
    for i in range(12, 21):
        if i < len(node_centers):
            arrow = FancyArrowPatch(node_centers[i], node_centers[21],
                                    arrowstyle='->', connectionstyle='arc3,rad=-0.2',
                                    color='#555', linewidth=1, linestyle='--', zorder=5)
            ax.add_patch(arrow)
    
    # Confirmation to reporting
    for i in [22, 23, 24]:
        arrow = FancyArrowPatch(node_centers[21], node_centers[i],
                                arrowstyle='->', connectionstyle='arc3,rad=0.1',
                                color='#555', linewidth=1.5, zorder=5)
        ax.add_patch(arrow)
    
    # Reporting to complete
    for i in [22, 23, 24]:
        arrow = FancyArrowPatch(node_centers[i], node_centers[25],
                                arrowstyle='->', connectionstyle='arc3,rad=0.15',
                                color='#555', linewidth=1.5, zorder=5)
        ax.add_patch(arrow)
    
    plt.tight_layout()
    output_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/vix-breach-architecture.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Diagram saved: {output_path}")
    plt.close()

if __name__ == '__main__':
    create_architecture_diagram()

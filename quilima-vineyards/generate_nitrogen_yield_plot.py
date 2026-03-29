#!/usr/bin/env python3
"""
Generate Nitrogen vs Yield visualization for Quilima Vineyards soil analysis.
Creates a scatter plot with trend line showing the relationship between
soil nitrogen levels and crop yield across four test zones.

Data Source: Quilima Vineyards soil analysis - Two harvest cycles
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.ticker import MaxNLocator

# ============================================
# EXACT DATA FROM SOIL ANALYSIS STUDY
# ============================================
# Zone identifiers
zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']

# Soil Nitrogen concentrations (mg/kg) - measured values
nitrogen_levels = [20, 18, 22, 19]

# Crop Yield (tonnes/hectare) - actual harvest measurements
yield_values = [4.5, 4.2, 4.8, 4.3]

# Soil pH values
ph_values = [6.8, 6.9, 6.7, 7.0]

# Baseline threshold
nitrogen_baseline = 15.0  # mg/kg

# ============================================
# Create figure with high resolution for publication
# ============================================
fig, ax = plt.subplots(figsize=(11, 8), dpi=150)

# Color scheme - professional agricultural science palette
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
zone_markers = ['o', 's', '^', 'D']

# Scatter plot for each zone
for i, zone in enumerate(zones):
    ax.scatter(
        nitrogen_levels[i], 
        yield_values[i],
        s=180,
        marker=zone_markers[i],
        facecolor=colors[i],
        edgecolor='black',
        linewidth=2,
        alpha=0.9,
        label=zone,
        zorder=5
    )
    
    # Add pH value annotation near each point
    ax.annotate(
        f'pH {ph_values[i]}',
        xy=(nitrogen_levels[i], yield_values[i]),
        xytext=(0, -18),
        textcoords='offset points',
        fontsize=8,
        ha='center',
        color='#555555',
        style='italic'
    )

# Add trend line (linear regression)
z = np.polyfit(nitrogen_levels, yield_values, 1)
p = np.poly1d(z)
x_line = np.linspace(14, 24, 100)
ax.plot(x_line, p(x_line), '--', color='#333333', linewidth=2.5, 
        label=f'Trend Line (r = {np.corrcoef(nitrogen_levels, yield_values)[0,1]:.3f})')

# Add baseline threshold line
ax.axvline(x=nitrogen_baseline, color='#C73E1D', linestyle='-', linewidth=2.5, 
           label=f'Nitrogen Baseline ({nitrogen_baseline} mg/kg)', zorder=3)

# Add shaded compliance zone (above baseline)
ax.axvspan(nitrogen_baseline, 24, alpha=0.15, color='green', 
           label='Compliance Zone (N > 15 mg/kg)', zorder=1)

# Annotate each zone with exact values
for i, zone in enumerate(zones):
    # Calculate compliance margin
    compliance_margin = ((nitrogen_levels[i] - nitrogen_baseline) / nitrogen_baseline) * 100
    
    # Position annotations to avoid overlap
    if i == 0:  # Zone A - top right
        xytext = (12, 8)
        ha, va = 'left', 'bottom'
    elif i == 1:  # Zone B - bottom left
        xytext = (-10, -25)
        ha, va = 'right', 'top'
    elif i == 2:  # Zone C - top right
        xytext = (12, 8)
        ha, va = 'left', 'bottom'
    else:  # Zone D - bottom right
        xytext = (12, -25)
        ha, va = 'left', 'top'
    
    ax.annotate(
        f'{zone}\nN: {nitrogen_levels[i]} mg/kg\nYield: {yield_values[i]} t/ha\nCompliance: +{compliance_margin:.0f}%',
        xy=(nitrogen_levels[i], yield_values[i]),
        xytext=xytext,
        textcoords='offset points',
        fontsize=9,
        ha=ha,
        va=va,
        bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                  edgecolor=colors[i], linewidth=2, alpha=0.95),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.2',
                       color=colors[i], linewidth=1.5, linestyle='-'),
        zorder=10
    )

# Labels and title
ax.set_xlabel('Soil Nitrogen Concentration (mg/kg)', fontsize=13, fontweight='bold', labelpad=10)
ax.set_ylabel('Crop Yield (tonnes/hectare)', fontsize=13, fontweight='bold', labelpad=10)
ax.set_title('Quilima Vineyards: Nitrogen-Yield Relationship Across Test Zones\nOrganic Grain Rotation Initiative - Two Harvest Cycles', 
             fontsize=14, fontweight='bold', pad=20)

# Axis formatting
ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=11))
ax.yaxis.set_major_locator(MaxNLocator(integer=False, nbins=8))
ax.set_xlim(14, 24)
ax.set_ylim(3.8, 5.2)

# Grid
ax.grid(True, linestyle='--', alpha=0.5, linewidth=0.8, color='#CCCCCC')
ax.set_axisbelow(True)

# Legend - position outside plot to avoid obscuring data
legend = ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), 
                   frameon=True, fancybox=True, shadow=True, 
                   fontsize=10, framealpha=0.95, ncol=2)
legend.get_frame().set_edgecolor('gray')
legend.get_frame().set_linewidth(0.8)

# Add statistical summary box
correlation = np.corrcoef(nitrogen_levels, yield_values)[0,1]
stats_text = 'Statistical Summary\n' + \
             '━━━━━━━━━━━━━━━━━━━━━━━━━━\n' + \
             f'Mean Nitrogen:  {np.mean(nitrogen_levels):.1f} mg/kg\n' + \
             f'Mean Yield:     {np.mean(yield_values):.2f} t/ha\n' + \
             f'Correlation:    r = {correlation:.3f}\n' + \
             f'pH Range:       {min(ph_values)} - {max(ph_values)}\n' + \
             f'Compliance:     100% (4/4 zones)\n' + \
             f'Baseline:       15 mg/kg'

props = dict(boxstyle='round,pad=0.6', facecolor='#F0F8FF', alpha=0.95, linewidth=2, edgecolor='#2E86AB')
ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace',
        bbox=props, linespacing=1.5, zorder=10)

# Add data table at bottom
table_data = [
    ['Zone', 'Nitrogen (mg/kg)', 'pH', 'Yield (t/ha)', 'Compliance'],
    ['A', '20', '6.8', '4.5', '+33%'],
    ['B', '18', '6.9', '4.2', '+20%'],
    ['C', '22', '6.7', '4.8', '+47%'],
    ['D', '19', '7.0', '4.3', '+27%'],
    ['Mean', '19.75', '6.85', '4.45', '+32%']
]

# Create table below the plot
ax_table = fig.add_axes([0.1, 0.02, 0.8, 0.12])
ax_table.axis('off')
table = ax_table.table(
    cellText=table_data[1:],
    colLabels=table_data[0],
    loc='center',
    cellLoc='center',
    colColours=['#2E86AB', '#2E86AB', '#2E86AB', '#2E86AB', '#2E86AB'],
    colWidths=[0.15, 0.2, 0.15, 0.2, 0.15]
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1.2, 1.8)

# Style table cells
for i in range(len(table_data)):
    for j in range(5):
        cell = table[(i, j)]
        if i == 0:  # Header row
            cell.set_text_props(weight='bold', color='white')
        elif i == len(table_data) - 1:  # Mean row
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#E8F4F8')
        else:
            cell.set_facecolor('#FFFFFF' if i % 2 == 1 else '#F5F5F5')
        cell.set_edgecolor('#CCCCCC')
        cell.set_linewidth(1)

# Add footer note
fig.text(0.5, 0.005, 
         'Data Source: Quilima Vineyards Soil Analysis - Two Harvest Cycles | All zones exceed 15 mg/kg nitrogen baseline',
         ha='center', fontsize=9, style='italic', color='#666666', weight='bold')

# Tight layout
plt.tight_layout(rect=[0, 0.15, 0.98, 1])

# Save figure
output_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/quilima-vineyards/nitrogen_yield_relationship.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f'SAVED: {output_path}')

# Also save as PDF for publication
pdf_path = '/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/quilima-vineyards/nitrogen_yield_relationship.pdf'
plt.savefig(pdf_path, dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print(f'SAVED: {pdf_path}')

plt.close()
print('Visualization generation complete.')
print(f'Correlation coefficient: r = {correlation:.3f}')

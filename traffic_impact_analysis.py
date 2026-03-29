#!/usr/bin/env python3
"""
Riverside District Traffic Impact Assessment

Analyzes gate capacities and utilization percentages for three access points.
Identifies which gates breach the 80% utilization threshold rule.

Run weekly to monitor projected traffic against designed capacities.
"""

from datetime import datetime

# ==============================================================================
# CONFIGURATION - Update these values with actual project data
# ==============================================================================

# Access point data: (Name, Designed Capacity, Projected Usage)
# Capacity and usage in vehicles per hour (vph)
ACCESS_POINTS = [
    {"name": "North Gate", "designed_capacity": 1500, "projected_usage": 1200},
    {"name": "South Plaza", "designed_capacity": 1200, "projected_usage": 850},
    {"name": "East Connector", "designed_capacity": 1750, "projected_usage": 1400},
]

# Utilization threshold for approval (80% rule)
UTILIZATION_THRESHOLD = 0.80

# ==============================================================================
# ANALYSIS FUNCTIONS
# ==============================================================================

def calculate_utilization(projected_usage, designed_capacity):
    """Calculate utilization percentage."""
    if designed_capacity == 0:
        return float('inf')
    return (projected_usage / designed_capacity) * 100

def get_approval_status(utilization_pct, threshold=UTILIZATION_THRESHOLD):
    """Determine approval status based on utilization threshold."""
    if utilization_pct >= threshold * 100:
        return "⚠️ BREACH"
    return "✅ APPROVED"

def analyze_traffic_impact():
    """Perform traffic impact analysis for all access points."""
    results = []
    
    for point in ACCESS_POINTS:
        utilization = calculate_utilization(
            point["projected_usage"], 
            point["designed_capacity"]
        )
        status = get_approval_status(utilization)
        
        results.append({
            "name": point["name"],
            "designed_capacity": point["designed_capacity"],
            "projected_usage": point["projected_usage"],
            "utilization_pct": utilization,
            "status": status,
            "breaches_threshold": utilization >= UTILIZATION_THRESHOLD * 100
        })
    
    return results

def print_analysis_report(results):
    """Print formatted analysis report with comparison table."""
    print("\n" + "=" * 80)
    print("  RIVERSIDE DISTRICT TRAFFIC IMPACT ASSESSMENT")
    print("  Weekly Automated Analysis Report")
    print("=" * 80)
    print(f"\n  Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Utilization Threshold: {UTILIZATION_THRESHOLD * 100:.0f}%")
    print("\n" + "-" * 80)
    
    # Table header
    print(f"\n  {'Access Point':<20} {'Designed Cap.':>14} {'Projected':>12} {'Util %':>10} {'Status':>15}")
    print(f"  {'-'*20} {'-'*14} {'-'*12} {'-'*10} {'-'*15}")
    
    # Table rows
    for result in results:
        print(f"  {result['name']:<20} {result['designed_capacity']:>14,} {result['projected_usage']:>12,} {result['utilization_pct']:>9.1f}% {result['status']:>15}")
    
    print("\n" + "-" * 80)
    
    # Summary statistics
    total_capacity = sum(r["designed_capacity"] for r in results)
    total_usage = sum(r["projected_usage"] for r in results)
    overall_utilization = (total_usage / total_capacity * 100) if total_capacity > 0 else 0
    breach_count = sum(1 for r in results if r["breaches_threshold"])
    
    print(f"\n  SUMMARY:")
    print(f"  ─────────────────────────────────────────────────────────────────────")
    print(f"  Total Designed Capacity:  {total_capacity:,}")
    print(f"  Total Projected Usage:    {total_usage:,}")
    print(f"  Overall Utilization:      {overall_utilization:.1f}%")
    print(f"  Gates Breaching 80% Rule: {breach_count} of {len(results)}")
    
    # Breach details
    breaches = [r for r in results if r["breaches_threshold"]]
    if breaches:
        print(f"\n  ⚠️  ATTENTION REQUIRED - Gates Exceeding 80% Threshold:")
        print(f"  ─────────────────────────────────────────────────────────────────────")
        for breach in breaches:
            excess = breach["utilization_pct"] - (UTILIZATION_THRESHOLD * 100)
            print(f"      • {breach['name']}: {breach['utilization_pct']:.1f}% ({excess:.1f}% over threshold)")
            print(f"        Capacity: {breach['designed_capacity']:,} | Projected: {breach['projected_usage']:,}")
    else:
        print(f"\n  ✅ All access points within acceptable utilization limits.")
    
    print("\n" + "=" * 80)
    print("  END OF REPORT")
    print("=" * 80 + "\n")

def save_results_to_file(results, output_path=None):
    """Optionally save results to JSON file for downstream processing."""
    import json
    
    if output_path is None:
        output_path = "/mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/logs/traffic_impact_results.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "threshold": UTILIZATION_THRESHOLD,
        "results": results,
        "summary": {
            "total_capacity": sum(r["designed_capacity"] for r in results),
            "total_usage": sum(r["projected_usage"] for r in results),
            "breach_count": sum(1 for r in results if r["breaches_threshold"])
        }
    }
    
    with open(output_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    return output_path

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

if __name__ == "__main__":
    print("\n🚦 Riverside District Traffic Impact Analysis")
    print("   Processing access point data...\n")
    
    # Run analysis
    results = analyze_traffic_impact()
    
    # Print formatted report
    print_analysis_report(results)
    
    # Save JSON results (optional, for automation pipelines)
    try:
        json_path = save_results_to_file(results)
        print(f"📄 Results saved to: {json_path}\n")
    except Exception as e:
        print(f"⚠️  Could not save JSON results: {e}\n")
    
    # Exit with appropriate code for cron monitoring
    breach_count = sum(1 for r in results if r["breaches_threshold"])
    if breach_count > 0:
        exit(1)  # Non-zero exit indicates attention needed
    else:
        exit(0)  # Clean exit indicates all clear

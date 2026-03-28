#!/usr/bin/env python3
"""
Currency Pair Monitoring Script
Q1 2026 - Automated breach detection for spot rate shifts > 5%

Usage: python currency_monitor.py [--baseline-file BASLINE_FILE]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Default configuration
DEFAULT_BASELINES = {
    "USD/EUR": 0.91,
    "GBP/USD": 1.26,
    "JPY/USD": 110.00
}

TOLERANCE_THRESHOLD = 5.0  # 5%

# In production, replace this with actual API calls to your rate provider
# Examples: exchangerate-api.com, fixer.io, open-exchange-rates.org
def fetch_current_spot_rates():
    """
    Fetch current spot rates from your preferred rate provider.
    Replace this stub with actual API integration.
    """
    # TODO: Replace with actual API call
    # Example using requests:
    # import requests
    # response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
    # data = response.json()
    # return {
    #     "USD/EUR": data["rates"]["EUR"],
    #     "GBP/USD": 1 / data["rates"]["GBP"],
    #     "JPY/USD": 1 / data["rates"]["JPY"]
    # }
    
    # Stub values for testing
    return {
        "USD/EUR": 0.92,
        "GBP/USD": 1.27,
        "JPY/USD": 110.50
    }


def calculate_variance(spot_rate, baseline):
    """Calculate variance percentage from baseline."""
    return ((spot_rate - baseline) / baseline) * 100


def check_breaches(spot_rates, baselines, threshold=TOLERANCE_THRESHOLD):
    """
    Check all currency pairs for breaches against baselines.
    
    Returns:
        dict: Analysis results with breaches and summary
    """
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "threshold": threshold,
        "pairs": [],
        "breaches": [],
        "summary": {
            "total_pairs": 0,
            "breaches_detected": 0,
            "status": "CLEAR"
        }
    }
    
    for pair, spot_rate in spot_rates.items():
        baseline = baselines.get(pair)
        if baseline is None:
            print(f"WARNING: No baseline configured for {pair}")
            continue
        
        variance = calculate_variance(spot_rate, baseline)
        is_breach = abs(variance) > threshold
        
        pair_result = {
            "pair": pair,
            "spot_rate": spot_rate,
            "baseline": baseline,
            "variance_pct": round(variance, 2),
            "is_breach": is_breach,
            "status": "BREACH" if is_breach else "OK"
        }
        
        results["pairs"].append(pair_result)
        results["summary"]["total_pairs"] += 1
        
        if is_breach:
            results["breaches"].append(pair_result)
            results["summary"]["breaches_detected"] += 1
    
    if results["summary"]["breaches_detected"] > 0:
        results["summary"]["status"] = "ALERT"
    
    return results


def generate_alert(breach_results):
    """Generate alert message for detected breaches."""
    alert_lines = [
        "🚨 CURRENCY RATE BREACH ALERT 🚨",
        f"Timestamp: {breach_results['timestamp']}",
        f"Threshold: {breach_results['threshold']}%",
        "",
        "Breaches Detected:"
    ]
    
    for breach in breach_results["breaches"]:
        direction = "↑" if breach["variance_pct"] > 0 else "↓"
        alert_lines.append(
            f"  {breach['pair']}: {breach['spot_rate']} "
            f"(baseline: {breach['baseline']}, variance: {direction} {abs(breach['variance_pct']):.2f}%)"
        )
    
    alert_lines.extend([
        "",
        "Action Required: Review and assess risk mitigation options."
    ])
    
    return "\n".join(alert_lines)


def save_report(results, output_dir="reports"):
    """Save analysis report to file."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    report_file = output_path / f"currency_report_{timestamp}.json"
    
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    
    return report_file


def main():
    """Main monitoring routine."""
    print("=" * 60)
    print("Currency Pair Monitoring - Breach Detection")
    print("=" * 60)
    
    # Fetch current rates
    print("\nFetching current spot rates...")
    spot_rates = fetch_current_spot_rates()
    
    # Load baselines (could be from file in production)
    baselines = DEFAULT_BASELINES
    print(f"Using {len(baselines)} baseline configurations")
    
    # Check for breaches
    print(f"Checking against {TOLERANCE_THRESHOLD}% tolerance threshold...\n")
    results = check_breaches(spot_rates, baselines)
    
    # Display results
    for pair in results["pairs"]:
        status_icon = "❌" if pair["is_breach"] else "✅"
        direction = "↑" if pair["variance_pct"] > 0 else ("↓" if pair["variance_pct"] < 0 else "→")
        print(f"{status_icon} {pair['pair']}: {pair['spot_rate']} "
              f"(variance: {direction} {abs(pair['variance_pct']):.2f}%)")
    
    print("\n" + "=" * 60)
    print(f"Summary: {results['summary']['breaches_detected']}/{results['summary']['total_pairs']} breaches")
    print(f"Status: {results['summary']['status']}")
    print("=" * 60)
    
    # Generate alert if breaches detected
    if results["summary"]["status"] == "ALERT":
        alert = generate_alert(results)
        print("\n" + alert)
        
        # TODO: Integrate with your alerting system
        # - Send email via SMTP
        # - Post to Slack webhook
        # - Send PagerDuty alert
        # - Write to monitoring system
    
    # Save report
    report_file = save_report(results)
    print(f"\nReport saved: {report_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results["summary"]["status"] == "CLEAR" else 1)


if __name__ == "__main__":
    main()

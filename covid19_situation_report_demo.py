#!/usr/bin/env python3
"""
COVID-19 Situation Report Generator - DEMO VERSION
Uses mock data for testing without API access.

Run this to see the script in action before connecting to your real API.
"""

import json
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
import statistics

# Import the analysis and report classes from the main script
from covid19_situation_report import (
    DailyCaseData,
    SituationReport,
    StatisticalAnalyzer,
    ReportGenerator,
    OUTPUT_CONFIG
)


def generate_mock_data(days: int = 7) -> List[DailyCaseData]:
    """Generate realistic mock COVID-19 data for testing."""
    
    # Base values with some variation
    base_cases = 1500
    base_deaths = 25
    base_recoveries = 1200
    base_tests = 50000
    
    data = []
    end_date = datetime.now()
    
    for i in range(days - 1, -1, -1):
        date = end_date - timedelta(days=i)
        
        # Add some realistic variation and a slight upward trend
        variation = 0.8 + (i / days) * 0.4  # Slight increase over time
        
        daily_data = DailyCaseData(
            date=date.strftime("%Y-%m-%d"),
            new_cases=int(base_cases * variation * (0.8 + 0.4 * (i % 3) / 3)),
            new_deaths=int(base_deaths * (0.7 + 0.6 * (i % 2))),
            new_recoveries=int(base_recoveries * variation),
            total_cases=1250000 + i * 1500,
            total_deaths=12500 + i * 25,
            total_recoveries=1100000 + i * 1200,
            active_cases=137500,
            tests_conducted=int(base_tests * (0.9 + 0.2 * (i % 4) / 4)),
            positivity_rate=2.5 + (i % 3) * 0.5,
            region="National"
        )
        data.append(daily_data)
    
    return data


def main():
    """Run the demo with mock data."""
    print("=" * 60)
    print("COVID-19 Situation Report Generator - DEMO MODE")
    print("=" * 60)
    print()
    print("ℹ️  This demo uses mock data. Connect to your real API")
    print("   by configuring covid19_situation_report.py")
    print()
    
    # Generate mock data
    print("📊 Generating mock data for last 7 days...")
    daily_data = generate_mock_data(days=7)
    print(f"✅ Generated {len(daily_data)} days of mock data")
    print()
    
    # Analyze data
    print("📈 Performing statistical analysis...")
    analyzer = StatisticalAnalyzer()
    report = analyzer.analyze(daily_data)
    print("✅ Analysis complete")
    print()
    
    # Generate reports
    print("📝 Generating reports...")
    generator = ReportGenerator(OUTPUT_CONFIG)
    saved_files = generator.save_report(report, daily_data)
    
    print(f"✅ Reports saved:")
    for format_type, path in saved_files.items():
        print(f"   - {format_type.upper()}: {path}")
    print()
    
    # Print summary
    print("=" * 60)
    print("7-DAY SITUATION SUMMARY")
    print("=" * 60)
    print(f"📅 Period: {report.period_start} to {report.period_end}")
    print(f"🦠 Total New Cases: {report.total_new_cases:,}")
    print(f"💀 Total New Deaths: {report.total_new_deaths:,}")
    print(f"✅ Total New Recoveries: {report.total_new_recoveries:,}")
    print(f"🧪 Total Tests: {report.total_tests:,}")
    print()
    print(f"📊 Average Daily Cases: {report.avg_daily_cases:,.1f}")
    print(f"📈 Case Trend: {report.case_trend.upper()} ({report.trend_percentage:+.1f}%)")
    print(f"🔝 Peak Day: {report.peak_day} ({report.peak_cases:,} cases)")
    print()
    print(f"⚠️  Case Fatality Rate: {report.case_fatality_rate:.2f}%")
    print(f"✅ Recovery Rate: {report.recovery_rate:.2f}%")
    print(f"🧪 Tests Per Case: {report.tests_per_case:,.1f}")
    print("=" * 60)
    print()
    print("💡 To use with real data:")
    print("   1. Update API_CONFIG in covid19_situation_report.py")
    print("   2. Set COVID_API_KEY environment variable")
    print("   3. Run: python covid19_situation_report.py")


if __name__ == "__main__":
    main()

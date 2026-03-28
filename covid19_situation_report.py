#!/usr/bin/env python3
"""
COVID-19 Situation Report Generator
Fetches data from national surveillance API and generates 7-day statistical analysis.

Author: OpenClaw Agent
Created: 2026-03-28
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import statistics
from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# CONFIGURATION - Update these values for your deployment
# ============================================================================

API_CONFIG = {
    "base_url": "https://api.covid-surveillance.gov.cn",  # Replace with actual API URL
    "endpoint": "/api/v1/cases/daily",
    "api_key": "",  # Set via environment variable or config file
    "timeout": 30,
    "retry_attempts": 3,
}

OUTPUT_CONFIG = {
    "output_dir": Path("./reports"),
    "filename_template": "covid19_situation_report_{date}.md",
    "include_json": True,
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class DailyCaseData:
    """Represents daily COVID-19 case data."""
    date: str
    new_cases: int
    new_deaths: int
    new_recoveries: int
    total_cases: int
    total_deaths: int
    total_recoveries: int
    active_cases: int
    tests_conducted: int
    positivity_rate: float
    region: str = "National"


@dataclass
class SituationReport:
    """Aggregated situation report metrics."""
    report_date: str
    period_start: str
    period_end: str
    days_analyzed: int
    
    # Summary metrics
    total_new_cases: int
    total_new_deaths: int
    total_new_recoveries: int
    total_tests: int
    
    # Statistical metrics
    avg_daily_cases: float
    median_daily_cases: float
    std_dev_cases: float
    avg_daily_deaths: float
    avg_positivity_rate: float
    
    # Trend analysis
    case_trend: str  # "increasing", "decreasing", "stable"
    trend_percentage: float
    peak_day: str
    peak_cases: int
    
    # Derived metrics
    case_fatality_rate: float
    recovery_rate: float
    tests_per_case: float


# ============================================================================
# API CLIENT
# ============================================================================

class COVID19APIClient:
    """Client for fetching data from the national surveillance API."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        
        if config.get("api_key"):
            self.session.headers.update({
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            })
    
    def fetch_daily_cases(self, days: int = 7) -> List[DailyCaseData]:
        """
        Fetch daily case data for the specified number of days.
        
        Args:
            days: Number of days of historical data to fetch
            
        Returns:
            List of DailyCaseData objects
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "format": "json"
        }
        
        url = f"{self.config['base_url']}{self.config['endpoint']}"
        
        for attempt in range(self.config.get("retry_attempts", 3)):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config.get("timeout", 30)
                )
                response.raise_for_status()
                data = response.json()
                
                return self._parse_api_response(data)
                
            except requests.exceptions.RequestException as e:
                print(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt == self.config.get("retry_attempts", 3) - 1:
                    raise
                continue
        
        return []
    
    def _parse_api_response(self, data: Dict[str, Any]) -> List[DailyCaseData]:
        """Parse API response into DailyCaseData objects."""
        cases = []
        
        # Adjust field names based on your actual API response structure
        for item in data.get("data", []):
            case = DailyCaseData(
                date=item.get("date", ""),
                new_cases=item.get("new_cases", 0),
                new_deaths=item.get("new_deaths", 0),
                new_recoveries=item.get("new_recoveries", 0),
                total_cases=item.get("total_cases", 0),
                total_deaths=item.get("total_deaths", 0),
                total_recoveries=item.get("total_recoveries", 0),
                active_cases=item.get("active_cases", 0),
                tests_conducted=item.get("tests_conducted", 0),
                positivity_rate=item.get("positivity_rate", 0.0),
                region=item.get("region", "National")
            )
            cases.append(case)
        
        return sorted(cases, key=lambda x: x.date)


# ============================================================================
# STATISTICAL ANALYSIS
# ============================================================================

class StatisticalAnalyzer:
    """Performs statistical analysis on COVID-19 case data."""
    
    def analyze(self, daily_data: List[DailyCaseData]) -> SituationReport:
        """
        Generate comprehensive statistical analysis.
        
        Args:
            daily_data: List of daily case data
            
        Returns:
            SituationReport with all metrics
        """
        if not daily_data:
            raise ValueError("No data provided for analysis")
        
        # Extract metrics
        cases = [d.new_cases for d in daily_data]
        deaths = [d.new_deaths for d in daily_data]
        positivity_rates = [d.positivity_rate for d in daily_data]
        tests = [d.tests_conducted for d in daily_data]
        recoveries = [d.new_recoveries for d in daily_data]
        
        # Calculate summary statistics
        total_new_cases = sum(cases)
        total_new_deaths = sum(deaths)
        total_new_recoveries = sum(recoveries)
        total_tests = sum(tests)
        
        # Statistical measures
        avg_daily_cases = statistics.mean(cases) if cases else 0
        median_daily_cases = statistics.median(cases) if cases else 0
        std_dev_cases = statistics.stdev(cases) if len(cases) > 1 else 0
        avg_daily_deaths = statistics.mean(deaths) if deaths else 0
        avg_positivity_rate = statistics.mean(positivity_rates) if positivity_rates else 0
        
        # Trend analysis
        case_trend, trend_percentage = self._calculate_trend(cases)
        
        # Peak identification
        peak_idx = cases.index(max(cases)) if cases else 0
        peak_day = daily_data[peak_idx].date if daily_data else ""
        peak_cases = max(cases) if cases else 0
        
        # Derived metrics
        total_cases = sum(d.total_cases for d in daily_data[-1:]) if daily_data else 0
        case_fatality_rate = (total_new_deaths / total_new_cases * 100) if total_new_cases > 0 else 0
        recovery_rate = (total_new_recoveries / total_new_cases * 100) if total_new_cases > 0 else 0
        tests_per_case = (total_tests / total_new_cases) if total_new_cases > 0 else 0
        
        return SituationReport(
            report_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            period_start=daily_data[0].date if daily_data else "",
            period_end=daily_data[-1].date if daily_data else "",
            days_analyzed=len(daily_data),
            total_new_cases=total_new_cases,
            total_new_deaths=total_new_deaths,
            total_new_recoveries=total_new_recoveries,
            total_tests=total_tests,
            avg_daily_cases=avg_daily_cases,
            median_daily_cases=median_daily_cases,
            std_dev_cases=std_dev_cases,
            avg_daily_deaths=avg_daily_deaths,
            avg_positivity_rate=avg_positivity_rate,
            case_trend=case_trend,
            trend_percentage=trend_percentage,
            peak_day=peak_day,
            peak_cases=peak_cases,
            case_fatality_rate=case_fatality_rate,
            recovery_rate=recovery_rate,
            tests_per_case=tests_per_case
        )
    
    def _calculate_trend(self, values: List[int]) -> tuple:
        """
        Calculate trend direction and percentage change.
        
        Compares first half average to second half average.
        """
        if len(values) < 2:
            return "stable", 0.0
        
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid]) if values[:mid] else 0
        second_half_avg = statistics.mean(values[mid:]) if values[mid:] else 0
        
        if first_half_avg == 0:
            return "increasing" if second_half_avg > 0 else "stable", 0.0
        
        percentage_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if percentage_change > 10:
            return "increasing", percentage_change
        elif percentage_change < -10:
            return "decreasing", percentage_change
        else:
            return "stable", percentage_change


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generates formatted situation reports."""
    
    def __init__(self, output_config: Dict[str, Any]):
        self.output_config = output_config
        self.output_dir = Path(output_config.get("output_dir", "./reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_markdown(self, report: SituationReport, daily_data: List[DailyCaseData]) -> str:
        """Generate a Markdown-formatted situation report."""
        
        trend_emoji = {
            "increasing": "📈",
            "decreasing": "📉",
            "stable": "➡️"
        }.get(report.case_trend, "➡️")
        
        md = f"""# COVID-19 Situation Report

**Report Generated:** {report.report_date}  
**Analysis Period:** {report.period_start} to {report.period_end}  
**Days Analyzed:** {report.days_analyzed}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total New Cases | {report.total_new_cases:,} |
| Total New Deaths | {report.total_new_deaths:,} |
| Total New Recoveries | {report.total_new_recoveries:,} |
| Total Tests Conducted | {report.total_tests:,} |

### Key Findings

- **Case Trend:** {trend_emoji} {report.case_trend.upper()} ({report.trend_percentage:+.1f}%)
- **Average Daily Cases:** {report.avg_daily_cases:,.1f}
- **Peak Day:** {report.peak_day} ({report.peak_cases:,} cases)
- **Average Positivity Rate:** {report.avg_positivity_rate:.2f}%

---

## Statistical Analysis

### Case Statistics

| Measure | Value |
|---------|-------|
| Mean Daily Cases | {report.avg_daily_cases:,.1f} |
| Median Daily Cases | {report.median_daily_cases:,.0f} |
| Standard Deviation | {report.std_dev_cases:,.1f} |
| Coefficient of Variation | {(report.std_dev_cases/report.avg_daily_cases*100) if report.avg_daily_cases > 0 else 0:.1f}% |

### Derived Metrics

| Metric | Value |
|--------|-------|
| Case Fatality Rate (CFR) | {report.case_fatality_rate:.2f}% |
| Recovery Rate | {report.recovery_rate:.2f}% |
| Tests Per Case | {report.tests_per_case:,.1f} |
| Average Daily Deaths | {report.avg_daily_deaths:,.1f} |

---

## Daily Breakdown

| Date | New Cases | New Deaths | New Recoveries | Tests | Positivity |
|------|-----------|------------|----------------|-------|------------|
"""
        
        for day in daily_data:
            md += f"| {day.date} | {day.new_cases:,} | {day.new_deaths:,} | {day.new_recoveries:,} | {day.tests_conducted:,} | {day.positivity_rate:.2f}% |\n"
        
        md += f"""
---

## Trend Analysis

The 7-day case trend is **{report.case_trend}** with a {report.trend_percentage:+.1f}% change 
comparing the first half to the second half of the analysis period.

### Recommendations

"""
        
        if report.case_trend == "increasing":
            md += """- ⚠️ **Alert:** Cases are trending upward. Consider:
  - Increasing testing capacity
  - Reviewing public health measures
  - Enhancing contact tracing efforts
"""
        elif report.case_trend == "decreasing":
            md += """- ✅ **Positive:** Cases are trending downward. Continue:
  - Current public health measures
  - Monitoring for potential resurgence
  - Vaccination campaigns
"""
        else:
            md += """- ➡️ **Stable:** Cases remain stable. Maintain:
  - Current surveillance levels
  - Preparedness measures
  - Public communication efforts
"""
        
        md += """
---

*Report generated by COVID-19 Situation Report Generator*
"""
        
        return md
    
    def generate_json(self, report: SituationReport, daily_data: List[DailyCaseData]) -> Dict:
        """Generate JSON-formatted report data."""
        return {
            "metadata": {
                "report_date": report.report_date,
                "period_start": report.period_start,
                "period_end": report.period_end,
                "days_analyzed": report.days_analyzed,
                "generated_by": "COVID-19 Situation Report Generator v1.0"
            },
            "summary": {
                "total_new_cases": report.total_new_cases,
                "total_new_deaths": report.total_new_deaths,
                "total_new_recoveries": report.total_new_recoveries,
                "total_tests": report.total_tests
            },
            "statistics": {
                "avg_daily_cases": report.avg_daily_cases,
                "median_daily_cases": report.median_daily_cases,
                "std_dev_cases": report.std_dev_cases,
                "avg_daily_deaths": report.avg_daily_deaths,
                "avg_positivity_rate": report.avg_positivity_rate
            },
            "trends": {
                "case_trend": report.case_trend,
                "trend_percentage": report.trend_percentage,
                "peak_day": report.peak_day,
                "peak_cases": report.peak_cases
            },
            "derived_metrics": {
                "case_fatality_rate": report.case_fatality_rate,
                "recovery_rate": report.recovery_rate,
                "tests_per_case": report.tests_per_case
            },
            "daily_data": [
                {
                    "date": d.date,
                    "new_cases": d.new_cases,
                    "new_deaths": d.new_deaths,
                    "new_recoveries": d.new_recoveries,
                    "tests_conducted": d.tests_conducted,
                    "positivity_rate": d.positivity_rate
                }
                for d in daily_data
            ]
        }
    
    def save_report(self, report: SituationReport, daily_data: List[DailyCaseData]) -> Dict[str, Path]:
        """Save reports to files."""
        saved_files = {}
        
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save Markdown report
        md_content = self.generate_markdown(report, daily_data)
        md_filename = self.output_config.get("filename_template", "covid19_situation_report_{date}.md").format(
            date=date_str
        )
        md_path = self.output_dir / md_filename
        md_path.write_text(md_content)
        saved_files["markdown"] = md_path
        
        # Save JSON report if configured
        if self.output_config.get("include_json", True):
            json_content = self.generate_json(report, daily_data)
            json_path = self.output_dir / f"covid19_situation_report_{date_str}.json"
            json_path.write_text(json.dumps(json_content, indent=2))
            saved_files["json"] = json_path
        
        return saved_files


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def load_config_from_env() -> Dict[str, Any]:
    """Load API configuration from environment variables."""
    import os
    
    config = API_CONFIG.copy()
    config["api_key"] = os.environ.get("COVID_API_KEY", config["api_key"])
    config["base_url"] = os.environ.get("COVID_API_BASE_URL", config["base_url"])
    
    return config


def main():
    """Main execution function."""
    print("=" * 60)
    print("COVID-19 Situation Report Generator")
    print("=" * 60)
    print()
    
    # Load configuration
    config = load_config_from_env()
    print(f"📡 API Base URL: {config['base_url']}")
    print(f"📅 Analysis Period: Last 7 days")
    print()
    
    try:
        # Fetch data
        print("🔄 Fetching data from surveillance API...")
        client = COVID19APIClient(config)
        daily_data = client.fetch_daily_cases(days=7)
        
        if not daily_data:
            print("❌ No data received from API. Check configuration and API availability.")
            return
        
        print(f"✅ Successfully fetched {len(daily_data)} days of data")
        print()
        
        # Analyze data
        print("📊 Performing statistical analysis...")
        analyzer = StatisticalAnalyzer()
        report = analyzer.analyze(daily_data)
        print(f"✅ Analysis complete")
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
        print("SUMMARY")
        print("=" * 60)
        print(f"Period: {report.period_start} to {report.period_end}")
        print(f"Total New Cases: {report.total_new_cases:,}")
        print(f"Total New Deaths: {report.total_new_deaths:,}")
        print(f"Case Trend: {report.case_trend.upper()} ({report.trend_percentage:+.1f}%)")
        print(f"Average Daily Cases: {report.avg_daily_cases:,.1f}")
        print(f"Case Fatality Rate: {report.case_fatality_rate:.2f}%")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Could not connect to API server")
        print(f"   Details: {e}")
        print("\n💡 Check your API configuration and network connectivity.")
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Details: {e}")
        print("\n💡 Check your API key and permissions.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("\n💡 Please check the error details and configuration.")
        raise


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
COVID-19 Situation Report Generator
Fetches data from national surveillance API and generates 7-day statistical analysis.

Author: OpenClaw Agent
Created: 2026-03-28
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import statistics
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION - Update these values for your deployment
# ============================================================================

API_CONFIG = {
    "base_url": "http://10.110.120.45:8080",
    "endpoint": "/v2/cases/daily",
    "api_key": "HS-2024-EPI-K3Y9B7N2P5R8",
    "timeout": 30,
    "retry_attempts": 3,
}

OUTPUT_CONFIG = {
    "output_dir": Path("./reports"),
    "filename_template": "covid19_situation_report_{date}.md",
    "include_json": True,
}

FALLBACK_CONFIG = {
    "enabled": True,
    "sample_data_file": Path("./sample_data.json"),
    "warning_message": """
⚠️  WARNING: API unreachable - using fallback sample data
   This report is based on SAMPLE DATA, not live API data.
   Please verify API connectivity before using for decision-making.
"""
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class DailyCaseData:
    """Represents daily COVID-19 case data."""
    date: str
    confirmed_cases: int
    deaths: int
    recovered: int
    hospitalized: int
    tests_conducted: int
    vaccinations_administered: int
    total_cases: int = 0
    total_deaths: int = 0
    total_recoveries: int = 0
    positivity_rate: float = 0.0
    region: str = "National"
    
    @property
    def new_cases(self) -> int:
        """Alias for confirmed_cases (daily new confirmed)."""
        return self.confirmed_cases
    
    @property
    def new_deaths(self) -> int:
        """Alias for deaths (daily new deaths)."""
        return self.deaths
    
    @property
    def new_recoveries(self) -> int:
        """Alias for recovered (daily new recoveries)."""
        return self.recovered
    
    @property
    def active_cases(self) -> int:
        """Calculated active cases."""
        return self.hospitalized


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
    total_vaccinations: int
    total_hospitalized: int
    
    # Statistical metrics
    avg_daily_cases: float
    median_daily_cases: float
    std_dev_cases: float
    avg_daily_deaths: float
    avg_positivity_rate: float
    avg_daily_vaccinations: float
    avg_daily_hospitalized: float
    
    # Trend analysis
    case_trend: str  # "increasing", "decreasing", "stable"
    trend_percentage: float
    peak_day: str
    peak_cases: int
    
    # Derived metrics
    case_fatality_rate: float
    recovery_rate: float
    tests_per_case: float
    hospitalization_rate: float
    vaccination_coverage: float


# ============================================================================
# API CLIENT
# ============================================================================

class COVID19APIClient:
    """Client for fetching data from the national surveillance API with fallback support."""
    
    def __init__(self, config: Dict[str, Any], fallback_config: Optional[Dict[str, Any]] = None):
        self.config = config
        self.fallback_config = fallback_config or FALLBACK_CONFIG
        self.session = requests.Session()
        self.data_source = "api"  # Track whether data came from API or fallback
        
        if config.get("api_key"):
            self.session.headers.update({
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            })
    
    def fetch_daily_cases(self, days: int = 7) -> List[DailyCaseData]:
        """
        Fetch daily case data for the specified number of days.
        Falls back to local sample data if API is unreachable.
        
        Args:
            days: Number of days of historical data to fetch
            
        Returns:
            List of DailyCaseData objects
        """
        # Try API first
        api_data, api_error = self._fetch_from_api(days)
        
        if api_data:
            self.data_source = "api"
            logger.info("✅ Successfully fetched data from API")
            return api_data
        
        # API failed - try fallback
        if self.fallback_config.get("enabled", True):
            logger.warning(f"⚠️  API request failed: {api_error}")
            fallback_data = self._load_fallback_data()
            if fallback_data:
                self.data_source = "fallback"
                logger.warning(FALLBACK_CONFIG["warning_message"])
                logger.info(f"📁 Loaded {len(fallback_data)} days of sample data from {self.fallback_config['sample_data_file']}")
                return fallback_data
        
        # No data available
        logger.error("❌ No data available - API failed and no fallback data found")
        raise RuntimeError(f"Failed to fetch data from API and fallback unavailable: {api_error}")
    
    def _fetch_from_api(self, days: int = 7) -> Tuple[Optional[List[DailyCaseData]], Optional[str]]:
        """
        Fetch data from API. Returns (data, None) on success or (None, error_message) on failure.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "format": "json"
        }
        
        url = f"{self.config['base_url']}{self.config['endpoint']}"
        
        logger.info(f"📡 Request URL: {url}")
        logger.info(f"📅 Date Range: {params['start_date']} to {params['end_date']}")
        api_key = self.config.get('api_key', '')
        if api_key:
            logger.info(f"🔑 API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 4 else ''}")
        
        for attempt in range(self.config.get("retry_attempts", 3)):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{self.config.get('retry_attempts', 3)}...")
                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config.get("timeout", 30)
                )
                
                logger.info(f"📥 Response Status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                parsed_data = self._parse_api_response(data)
                if parsed_data:
                    return (parsed_data, None)
                else:
                    return (None, "API returned empty data")
                
            except requests.exceptions.JSONDecodeError as e:
                error_msg = f"JSON Decode Error: {e}"
                logger.error(f"❌ {error_msg}")
                if attempt == self.config.get("retry_attempts", 3) - 1:
                    return (None, error_msg)
                continue
            except requests.exceptions.HTTPError as e:
                error_msg = f"HTTP Error {e.response.status_code}: {e}"
                logger.error(f"❌ {error_msg}")
                if attempt == self.config.get("retry_attempts", 3) - 1:
                    return (None, error_msg)
                continue
            except requests.exceptions.ConnectionError as e:
                error_msg = f"Connection Error: {e}"
                logger.error(f"❌ {error_msg}")
                if attempt == self.config.get("retry_attempts", 3) - 1:
                    return (None, error_msg)
                continue
            except requests.exceptions.Timeout as e:
                error_msg = f"Timeout Error: {e}"
                logger.error(f"❌ {error_msg}")
                if attempt == self.config.get("retry_attempts", 3) - 1:
                    return (None, error_msg)
                continue
            except requests.exceptions.RequestException as e:
                error_msg = f"Request Error: {e}"
                logger.error(f"❌ {error_msg}")
                if attempt == self.config.get("retry_attempts", 3) - 1:
                    return (None, error_msg)
                continue
        
        return (None, "All retry attempts failed")
    
    def _load_fallback_data(self) -> Optional[List[DailyCaseData]]:
        """
        Load sample data from local JSON file.
        
        Returns:
            List of DailyCaseData objects or None if file not found
        """
        sample_file = Path(self.fallback_config.get("sample_data_file", "./sample_data.json"))
        
        if not sample_file.exists():
            logger.error(f"❌ Fallback file not found: {sample_file.absolute()}")
            return None
        
        try:
            with open(sample_file, 'r') as f:
                data = json.load(f)
            
            parsed_data = self._parse_api_response(data)
            
            if not parsed_data:
                logger.error("❌ Failed to parse fallback data")
                return None
            
            logger.info(f"✅ Successfully loaded fallback data from {sample_file}")
            return parsed_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in fallback file: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error loading fallback data: {e}")
            return None
    
    def _parse_api_response(self, data: Dict[str, Any]) -> List[DailyCaseData]:
        """Parse API response into DailyCaseData objects.
        
        Expected API response structure:
        {
            "data": [
                {
                    "date": "2026-03-28",
                    "confirmed_cases": 1523,
                    "deaths": 28,
                    "recovered": 1245,
                    "hospitalized": 450,
                    "tests_conducted": 50000,
                    "vaccinations_administered": 12000
                }
            ]
        }
        """
        cases = []
        
        for item in data.get("data", []):
            # Calculate positivity rate if both fields are available
            tests = item.get("tests_conducted", 0)
            confirmed = item.get("confirmed_cases", 0)
            positivity_rate = (confirmed / tests * 100) if tests > 0 else 0.0
            
            case = DailyCaseData(
                date=item.get("date", ""),
                confirmed_cases=item.get("confirmed_cases", 0),
                deaths=item.get("deaths", 0),
                recovered=item.get("recovered", 0),
                hospitalized=item.get("hospitalized", 0),
                tests_conducted=item.get("tests_conducted", 0),
                vaccinations_administered=item.get("vaccinations_administered", 0),
                positivity_rate=positivity_rate,
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
        cases = [d.confirmed_cases for d in daily_data]
        deaths = [d.deaths for d in daily_data]
        recoveries = [d.recovered for d in daily_data]
        hospitalized = [d.hospitalized for d in daily_data]
        tests = [d.tests_conducted for d in daily_data]
        vaccinations = [d.vaccinations_administered for d in daily_data]
        positivity_rates = [d.positivity_rate for d in daily_data]
        
        # Calculate summary statistics
        total_new_cases = sum(cases)
        total_new_deaths = sum(deaths)
        total_new_recoveries = sum(recoveries)
        total_tests = sum(tests)
        total_vaccinations = sum(vaccinations)
        total_hospitalized = sum(hospitalized)
        
        # Statistical measures
        avg_daily_cases = statistics.mean(cases) if cases else 0
        median_daily_cases = statistics.median(cases) if cases else 0
        std_dev_cases = statistics.stdev(cases) if len(cases) > 1 else 0
        avg_daily_deaths = statistics.mean(deaths) if deaths else 0
        avg_positivity_rate = statistics.mean(positivity_rates) if positivity_rates else 0
        avg_daily_vaccinations = statistics.mean(vaccinations) if vaccinations else 0
        avg_daily_hospitalized = statistics.mean(hospitalized) if hospitalized else 0
        
        # Trend analysis
        case_trend, trend_percentage = self._calculate_trend(cases)
        
        # Peak identification
        peak_idx = cases.index(max(cases)) if cases else 0
        peak_day = daily_data[peak_idx].date if daily_data else ""
        peak_cases = max(cases) if cases else 0
        
        # Derived metrics
        case_fatality_rate = (total_new_deaths / total_new_cases * 100) if total_new_cases > 0 else 0
        recovery_rate = (total_new_recoveries / total_new_cases * 100) if total_new_cases > 0 else 0
        tests_per_case = (total_tests / total_new_cases) if total_new_cases > 0 else 0
        hospitalization_rate = (sum(hospitalized) / total_new_cases * 100) if total_new_cases > 0 else 0
        vaccination_coverage = (total_vaccinations / total_new_cases) if total_new_cases > 0 else 0
        
        return SituationReport(
            report_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            period_start=daily_data[0].date if daily_data else "",
            period_end=daily_data[-1].date if daily_data else "",
            days_analyzed=len(daily_data),
            total_new_cases=total_new_cases,
            total_new_deaths=total_new_deaths,
            total_new_recoveries=total_new_recoveries,
            total_tests=total_tests,
            total_vaccinations=total_vaccinations,
            total_hospitalized=total_hospitalized,
            avg_daily_cases=avg_daily_cases,
            median_daily_cases=median_daily_cases,
            std_dev_cases=std_dev_cases,
            avg_daily_deaths=avg_daily_deaths,
            avg_positivity_rate=avg_positivity_rate,
            avg_daily_vaccinations=avg_daily_vaccinations,
            avg_daily_hospitalized=avg_daily_hospitalized,
            case_trend=case_trend,
            trend_percentage=trend_percentage,
            peak_day=peak_day,
            peak_cases=peak_cases,
            case_fatality_rate=case_fatality_rate,
            recovery_rate=recovery_rate,
            tests_per_case=tests_per_case,
            hospitalization_rate=hospitalization_rate,
            vaccination_coverage=vaccination_coverage
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
| Total Confirmed Cases | {report.total_new_cases:,} |
| Total Deaths | {report.total_new_deaths:,} |
| Total Recovered | {report.total_new_recoveries:,} |
| Total Hospitalized | {report.total_hospitalized:,} |
| Total Tests Conducted | {report.total_tests:,} |
| Total Vaccinations Administered | {report.total_vaccinations:,} |

### Key Findings

- **Case Trend:** {trend_emoji} {report.case_trend.upper()} ({report.trend_percentage:+.1f}%)
- **Average Daily Cases:** {report.avg_daily_cases:,.1f}
- **Peak Day:** {report.peak_day} ({report.peak_cases:,} cases)
- **Average Positivity Rate:** {report.avg_positivity_rate:.2f}%
- **Average Daily Vaccinations:** {report.avg_daily_vaccinations:,.0f}

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
| Hospitalization Rate | {report.hospitalization_rate:.2f}% |
| Tests Per Case | {report.tests_per_case:,.1f} |
| Vaccination Coverage (doses/case) | {report.vaccination_coverage:.1f} |
| Average Daily Deaths | {report.avg_daily_deaths:,.1f} |
| Average Daily Hospitalized | {report.avg_daily_hospitalized:,.0f} |

---

## Daily Breakdown

| Date | Confirmed | Deaths | Recovered | Hospitalized | Tests | Vaccinations |
|------|-----------|--------|-----------|--------------|-------|--------------|
"""
        
        for day in daily_data:
            md += f"| {day.date} | {day.confirmed_cases:,} | {day.deaths:,} | {day.recovered:,} | {day.hospitalized:,} | {day.tests_conducted:,} | {day.vaccinations_administered:,} |\n"
        
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
                "total_hospitalized": report.total_hospitalized,
                "total_tests": report.total_tests,
                "total_vaccinations": report.total_vaccinations
            },
            "statistics": {
                "avg_daily_cases": report.avg_daily_cases,
                "median_daily_cases": report.median_daily_cases,
                "std_dev_cases": report.std_dev_cases,
                "avg_daily_deaths": report.avg_daily_deaths,
                "avg_positivity_rate": report.avg_positivity_rate,
                "avg_daily_vaccinations": report.avg_daily_vaccinations,
                "avg_daily_hospitalized": report.avg_daily_hospitalized
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
                "hospitalization_rate": report.hospitalization_rate,
                "tests_per_case": report.tests_per_case,
                "vaccination_coverage": report.vaccination_coverage
            },
            "daily_data": [
                {
                    "date": d.date,
                    "confirmed_cases": d.confirmed_cases,
                    "deaths": d.deaths,
                    "recovered": d.recovered,
                    "hospitalized": d.hospitalized,
                    "tests_conducted": d.tests_conducted,
                    "vaccinations_administered": d.vaccinations_administered,
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
    print(f"📁 Fallback File: {FALLBACK_CONFIG['sample_data_file']}")
    print(f"📅 Analysis Period: Last 7 days")
    print()
    
    try:
        # Fetch data
        print("🔄 Fetching data from surveillance API...")
        client = COVID19APIClient(config, FALLBACK_CONFIG)
        daily_data = client.fetch_daily_cases(days=7)
        
        if not daily_data:
            print("❌ No data received. Check configuration and API availability.")
            return
        
        # Display data source
        if client.data_source == "api":
            print(f"✅ Successfully fetched {len(daily_data)} days of data from API")
        else:
            print(f"⚠️  Using {len(daily_data)} days of SAMPLE DATA (API unavailable)")
            print()
            print("=" * 60)
            print("⚠️  DISCLAIMER: SAMPLE DATA MODE")
            print("=" * 60)
            print("This report is based on SAMPLE DATA, not live API data.")
            print("Please verify API connectivity before using for decision-making.")
            print("=" * 60)
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
        print(f"Data Source: {client.data_source.upper()}")
        print(f"Period: {report.period_start} to {report.period_end}")
        print(f"Total Confirmed Cases: {report.total_new_cases:,}")
        print(f"Total Deaths: {report.total_new_deaths:,}")
        print(f"Total Recovered: {report.total_new_recoveries:,}")
        print(f"Total Hospitalized: {report.total_hospitalized:,}")
        print(f"Total Tests: {report.total_tests:,}")
        print(f"Total Vaccinations: {report.total_vaccinations:,}")
        print()
        print(f"Case Trend: {report.case_trend.upper()} ({report.trend_percentage:+.1f}%)")
        print(f"Average Daily Cases: {report.avg_daily_cases:,.1f}")
        print(f"Case Fatality Rate: {report.case_fatality_rate:.2f}%")
        print(f"Recovery Rate: {report.recovery_rate:.2f}%")
        print(f"Hospitalization Rate: {report.hospitalization_rate:.2f}%")
        print("=" * 60)
        
    except RuntimeError as e:
        print(f"❌ Data Fetch Error: {e}")
        print("\n💡 Ensure either:")
        print("   - API is accessible and credentials are valid, OR")
        print("   - Fallback file (sample_data.json) exists in the workspace")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        print("\n💡 Please check the error details and configuration.")
        logger.exception("Full traceback:")
        raise


if __name__ == "__main__":
    main()

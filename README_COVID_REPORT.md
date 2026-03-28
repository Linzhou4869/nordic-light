# COVID-19 Situation Report Generator

Automated 7-day COVID-19 situation report generation with statistical analysis.

## Quick Start

### 1. Test with Mock Data (Recommended First)

```bash
python covid19_situation_report_demo.py
```

This will generate sample reports without needing API access.

### 2. Configure for Production

Edit `covid19_situation_report.py` and update:

```python
API_CONFIG = {
    "base_url": "https://your-api-domain.gov",
    "endpoint": "/api/v1/cases/daily",
    "api_key": "your-api-key-here",
    "timeout": 30,
    "retry_attempts": 3,
}
```

Or use environment variables:

```bash
export COVID_API_KEY="your-api-key"
export COVID_API_BASE_URL="https://your-api-domain.gov"
python covid19_situation_report.py
```

## Output Files

Reports are saved to `./reports/`:

- `covid19_situation_report_YYYYMMDD_HHMMSS.md` - Human-readable Markdown report
- `covid19_situation_report_YYYYMMDD_HHMMSS.json` - Machine-readable JSON data

## Features

### Statistical Analysis
- 7-day rolling averages
- Trend detection (increasing/decreasing/stable)
- Standard deviation and variance analysis
- Peak day identification

### Key Metrics
- Case Fatality Rate (CFR)
- Recovery Rate
- Tests per Case
- Positivity Rate

### Report Sections
- Executive Summary
- Statistical Analysis Tables
- Daily Breakdown
- Trend Analysis
- Automated Recommendations

## API Response Format

The script expects JSON responses in this format:

```json
{
  "data": [
    {
      "date": "2026-03-28",
      "new_cases": 1523,
      "new_deaths": 28,
      "new_recoveries": 1245,
      "total_cases": 1250000,
      "total_deaths": 12500,
      "total_recoveries": 1100000,
      "active_cases": 137500,
      "tests_conducted": 50000,
      "positivity_rate": 3.05,
      "region": "National"
    }
  ]
}
```

Adjust the `_parse_api_response()` method if your API uses different field names.

## Customization

### Modify Analysis Period

```python
# In main() or fetch_daily_cases()
daily_data = client.fetch_daily_cases(days=14)  # 14 days instead of 7
```

### Change Output Location

```python
OUTPUT_CONFIG = {
    "output_dir": Path("/path/to/your/reports"),
    "filename_template": "covid_report_{date}.md",
    "include_json": True,
}
```

### Add Visualizations

Add matplotlib/plotly code to generate charts:

```python
import matplotlib.pyplot as plt

def generate_chart(daily_data):
    dates = [d.date for d in daily_data]
    cases = [d.new_cases for d in daily_data]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, cases, marker='o')
    plt.title('7-Day COVID-19 Cases')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('cases_chart.png')
```

## Scheduling

Run daily via cron:

```bash
# Add to crontab (runs at 8 AM daily)
0 8 * * * cd /path/to/workspace && /usr/bin/python3 covid19_situation_report.py
```

## Dependencies

```bash
pip install requests
```

Optional for visualizations:
```bash
pip install matplotlib plotly pandas
```

## Security Notes

- Store API keys in environment variables, not in code
- Set appropriate file permissions on output directory
- Review reports before distributing externally

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection Error | Check API URL and network connectivity |
| 401 Unauthorized | Verify API key is correct and not expired |
| 404 Not Found | Check endpoint path in API_CONFIG |
| No Data Received | Verify API response format matches expected structure |
| Permission Denied | Check write permissions on output directory |

## License

Internal use only - National Surveillance System

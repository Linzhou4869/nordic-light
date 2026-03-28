# Weekly Build Metrics Pipeline

Automated pipeline for collecting build success rates and latency metrics, generating comprehensive weekly reports.

## Schedule

- **When:** Every Monday at 9:00 AM JST (00:00 UTC)
- **Output:** Markdown report + JSON data files

## Quick Start

### 1. Install the Cron Job

```bash
# Install
crontab crontab-entry.txt

# Verify
crontab -l

# Test run (manual execution)
./weekly-build-pipeline.sh
```

### 2. Manual Test Run

```bash
./weekly-build-pipeline.sh
```

## Output Structure

```
workspace/
├── weekly-build-pipeline.sh    # Main pipeline script
├── crontab-entry.txt           # Cron schedule configuration
├── reports/                     # Generated reports
│   └── weekly-build-report-YYYY-MM-DD.md
├── data/                        # Raw metrics (JSON)
│   ├── build-metrics-*.json
│   └── latency-metrics-*.json
└── logs/                        # Execution logs
    ├── pipeline-*.log
    └── cron.log
```

## Metrics Collected

### Build Metrics
- Total builds executed
- Success/failure counts
- Success rate percentage
- Build duration (avg/min/max)
- Failure breakdown by type:
  - Compilation errors
  - Test failures
  - Dependency issues
  - Timeout errors

### Latency Metrics
- Build API latency (P95, P99, avg)
- Dependency download latency
- Test execution latency
- Infrastructure utilization (CPU, memory)

## Customization

### Add More Projects

Edit `weekly-build-pipeline.sh` and add:

```bash
collect_build_metrics "/path/to/another-project" "project-name"
```

### Configure Notifications

Uncomment the notification section in the script:

```bash
# Email
mail -s "Weekly Build Report: ${TODAY}" team@example.com < "${REPORT_FILE}"

# Slack (requires curl)
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"Weekly build report ready: ${REPORT_FILE}\"}" \
  $SLACK_WEBHOOK_URL
```

### Adjust Retention

Change the cleanup threshold (default: 30 days):

```bash
find "${DATA_DIR}" -name "*.json" -mtime +30 -delete
# Change +30 to your preferred retention period
```

## Report Format

Reports are generated in Markdown with:
- Executive summary with key metrics table
- Build success analysis
- Failure breakdown
- Latency & performance metrics
- Infrastructure utilization
- Dynamic recommendations
- Appendix with data file references

## Troubleshooting

### Check Logs

```bash
# Latest pipeline log
cat logs/pipeline-$(date +%Y-%m-%d).log

# Cron execution log
tail -f logs/cron.log
```

### Test Cron Syntax

```bash
# Validate crontab
crontab -l | grep weekly-build-pipeline

# Test cron schedule (next run)
date -d "next Monday"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Script not executable | `chmod +x weekly-build-pipeline.sh` |
| Timezone mismatch | Verify `TZ=Asia/Tokyo` in script |
| Missing directories | Script auto-creates on first run |
| Cron not running | `sudo systemctl status cron` |

## Dependencies

- Bash 4.0+
- `date` (GNU coreutils)
- `bc` (for calculations)
- `grep`, `sed` (for parsing)
- Optional: `jq` (for JSON manipulation)
- Optional: `mail` (for email notifications)

## Version History

- **v1.0** (2026-03-28): Initial implementation
  - Spring PetClinic metrics collection
  - JSON data export
  - Markdown report generation
  - Cron scheduling

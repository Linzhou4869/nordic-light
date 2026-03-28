# Currency Monitoring Setup

## Overview

Automated daily monitoring script for currency pair breach detection (>5% variance from baseline).

## Files

| File | Description |
|------|-------------|
| `currency_monitor.py` | Main monitoring script |
| `baselines.json` | Configurable baseline rates |
| `cron_setup.sh` | Cron installation helper |

## Cron Schedule

**Daily at 9:00 AM UTC:**

```cron
0 9 * * * /usr/bin/python3 /path/to/currency_monitor.py >> /var/log/currency_monitor.log 2>&1
```

### Cron Field Breakdown

| Field | Value | Meaning |
|-------|-------|---------|
| Minute | `0` | At minute 0 |
| Hour | `9` | At 9 AM |
| Day of Month | `*` | Every day |
| Month | `*` | Every month |
| Day of Week | `*` | Every day of week |

## Installation

### Option 1: Manual Cron Setup

```bash
# Edit crontab
crontab -e

# Add the following line (update path to script)
0 9 * * * /usr/bin/python3 /path/to/currency_monitor.py >> /var/log/currency_monitor.log 2>&1
```

### Option 2: Use Setup Script

```bash
chmod +x cron_setup.sh
./cron_setup.sh
```

### Option 3: Systemd Timer (Alternative)

For systems using systemd:

```bash
# Create timer unit
sudo cp currency-monitor.timer /etc/systemd/system/
sudo cp currency-monitor.service /etc/systemd/system/

# Enable and start
sudo systemctl enable currency-monitor.timer
sudo systemctl start currency-monitor.timer
```

## Configuration

### Update Baselines

Edit `baselines.json` to update baseline rates:

```json
{
  "USD/EUR": 0.91,
  "GBP/USD": 1.26,
  "JPY/USD": 110.00
}
```

### Update Tolerance Threshold

Edit `currency_monitor.py`:

```python
TOLERANCE_THRESHOLD = 5.0  # Change to desired percentage
```

## Alerting Integration

The script exits with code `1` when breaches are detected, enabling integration with:

- **Email**: Configure SMTP in `currency_monitor.py`
- **Slack**: Add webhook POST to `generate_alert()`
- **PagerDuty**: Use PagerDuty API for critical alerts
- **Monitoring tools**: Prometheus, Datadog, etc.

## Log Location

```
/var/log/currency_monitor.log
```

## Manual Testing

```bash
# Run manually to test
python3 currency_monitor.py

# Check exit code
echo $?  # 0 = CLEAR, 1 = ALERT
```

## Timezone Note

Cron runs in system timezone. To ensure 9 AM UTC:

```bash
# Check system timezone
timedatectl

# If not UTC, either:
# 1. Set system to UTC, or
# 2. Adjust cron hour for your timezone
```

---

*Last updated: 2026-03-28*

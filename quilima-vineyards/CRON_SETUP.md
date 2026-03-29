# Automated Nitrogen-Yield Plot Generation

## Overview

This directory contains a cron job configuration to automatically regenerate the nitrogen-yield relationship visualization every **Friday at 8:00 AM**.

## Files

| File | Purpose |
|------|---------|
| `generate_nitrogen_yield_plot.py` | Main script that generates the visualization |
| `crontab-entry.txt` | Cron job configuration file |
| `logs/cron.log` | Execution log (created on first run) |

## Installation

### Step 1: Verify Python and Dependencies

Ensure Python 3 and matplotlib are available:

```bash
python3 --version
python3 -c "import matplotlib; print(matplotlib.__version__)"
```

### Step 2: Install the Cron Job

```bash
crontab /mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/quilima-vineyards/crontab-entry.txt
```

### Step 3: Verify Installation

```bash
crontab -l
```

You should see the Friday 8 AM entry listed.

### Step 4: Test Manual Execution

Before relying on the scheduled run, test the script manually:

```bash
python3 /mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/quilima-vineyards/generate_nitrogen_yield_plot.py
```

## Schedule Details

| Field | Value | Meaning |
|-------|-------|---------|
| Minute | `0` | At the top of the hour |
| Hour | `8` | 8:00 AM |
| Day of Month | `*` | Every day |
| Month | `*` | Every month |
| Day of Week | `5` | Friday (0=Sunday, 5=Friday) |

## Output

On each run, the script generates:

- `nitrogen_yield_relationship.png` - High-resolution PNG (300 DPI)
- `nitrogen_yield_relationship.pdf` - Publication-ready PDF

## Monitoring

### Check Execution Logs

```bash
cat /mnt/afs_toolcall/zhoulin3/.openclaw/workspaces/gendata-worker-27/quilima-vineyards/logs/cron.log
```

### Check System Cron Logs

```bash
# Debian/Ubuntu
grep CRON /var/log/syslog | grep generate_nitrogen_yield

# RHEL/CentOS
grep CRON /var/log/cron | grep generate_nitrogen_yield

# systemd-based systems
journalctl -u cron | grep generate_nitrogen_yield
```

## Troubleshooting

### Script Not Running

1. Verify cron daemon is active: `systemctl status cron` or `systemctl status crond`
2. Check file permissions: `ls -la generate_nitrogen_yield_plot.py`
3. Test manual execution to rule out Python/matplotlib issues

### Permission Denied

Make the script executable:

```bash
chmod +x generate_nitrogen_yield_plot.py
```

### Missing Dependencies

Install required Python packages:

```bash
pip3 install matplotlib numpy
```

## Removal

To remove the cron job:

```bash
crontab -l | grep -v "generate_nitrogen_yield_plot.py" | crontab -
```

Verify removal:

```bash
crontab -l
```

---

**Last Updated:** 2026-03-29  
**Next Scheduled Run:** Friday, 2026-04-03 at 8:00 AM

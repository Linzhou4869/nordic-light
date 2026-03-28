#!/bin/bash
# Currency Monitor Cron Setup Script
# Installs daily 9 AM UTC monitoring job

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITOR_SCRIPT="$SCRIPT_DIR/currency_monitor.py"
LOG_DIR="/var/log"
LOG_FILE="$LOG_DIR/currency_monitor.log"
CRON_JOB="0 9 * * * /usr/bin/python3 $MONITOR_SCRIPT >> $LOG_FILE 2>&1"

echo "=============================================="
echo "Currency Monitor - Cron Setup"
echo "=============================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "WARNING: Not running as root. Cron installation may fail."
fi

# Verify monitor script exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    echo "ERROR: Monitor script not found at $MONITOR_SCRIPT"
    exit 1
fi

# Create log directory if needed
if [ ! -d "$LOG_DIR" ]; then
    echo "Creating log directory: $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
fi

# Create log file if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    echo "Creating log file: $LOG_FILE"
    sudo touch "$LOG_FILE"
    sudo chmod 644 "$LOG_FILE"
fi

# Make monitor script executable
chmod +x "$MONITOR_SCRIPT"

# Install cron job
echo ""
echo "Installing cron job:"
echo "  $CRON_JOB"
echo ""

# Check if cron is installed
if ! command -v crontab &> /dev/null; then
    echo "ERROR: crontab not found. Please install cron first."
    exit 1
fi

# Add to crontab (preserve existing jobs)
(crontab -l 2>/dev/null | grep -v "currency_monitor.py"; echo "$CRON_JOB") | crontab -

echo "=============================================="
echo "✓ Cron job installed successfully!"
echo "=============================================="
echo ""
echo "Verify with: crontab -l"
echo "Check logs:  tail -f $LOG_FILE"
echo "Test run:    python3 $MONITOR_SCRIPT"
echo ""

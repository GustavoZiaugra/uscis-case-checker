#!/bin/bash
# Install USCIS Case Checker cron job
# This script adds a daily cron job to check your USCIS case status

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_COMMENT="# USCIS Case Status Checker - Daily at 9 AM"
CRON_JOB="0 9 * * * cd ${SCRIPT_DIR} && docker-compose up uscis-checker --abort-on-container-exit >> /var/log/uscis-checker.log 2>&1"

echo "=== USCIS Case Checker - Cron Installer ==="
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "uscis-checker"; then
    echo "⚠️  Cron job already exists!"
    echo ""
    echo "Current crontab entries for USCIS:"
    crontab -l | grep "uscis-checker" || true
    echo ""
    read -p "Remove existing and reinstall? (y/N): " reinstall
    if [[ $reinstall =~ ^[Yy]$ ]]; then
        # Remove existing entries
        crontab -l 2>/dev/null | grep -v "uscis-checker" | crontab -
        echo "✓ Removed existing cron job"
    else
        echo "Cancelled"
        exit 0
    fi
fi

# Check if .env file exists
if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create it first: cp .env.example .env"
    echo ""
    read -p "Continue anyway? (y/N): " continue
    if [[ ! $continue =~ ^[Yy]$ ]]; then
        echo "Cancelled"
        exit 1
    fi
fi

echo "Adding cron job..."
echo "  Schedule: Daily at 9:00 AM"
echo "  Command: ${CRON_JOB}"
echo ""

# Add to crontab
(crontab -l 2>/dev/null; echo ""; echo "${CRON_COMMENT}"; echo "${CRON_JOB}") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "To verify, run: crontab -l"
echo ""
echo "To start the services:"
echo "  cd ${SCRIPT_DIR} && docker-compose up -d"
echo ""
echo "To run a manual check:"
echo "  cd ${SCRIPT_DIR} && docker-compose up uscis-checker"

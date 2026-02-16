#!/usr/bin/env python3
"""
OpenClaw Skill: USCIS Case Checker
Automated USCIS case status monitoring with Cloudflare bypass
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Skill configuration
SKILL_NAME = "uscis-case-checker"
REPO_URL = "https://github.com/GustavoZiaugra/uscis-case-checker"
DATA_DIR = Path.home() / ".openclaw" / "uscis-checker"


def ensure_data_dir():
    """Ensure data directory exists"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        subprocess.run(["docker-compose", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def cmd_setup(case_number=None):
    """Set up USCIS case checker configuration"""
    print("🔧 Setting up USCIS Case Checker...")

    if not check_docker():
        print("❌ Error: Docker and Docker Compose are required")
        print("Please install Docker: https://docs.docker.com/get-docker/")
        return 1

    data_dir = ensure_data_dir()

    # Clone repository if not exists
    if not (data_dir / "docker-compose.yml").exists():
        print(f"📦 Downloading USCIS Checker...")
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(data_dir)], check=True
        )

    # Get case number if not provided
    if not case_number:
        case_number = input(
            "Enter your USCIS case number (e.g., IOE1234567890): "
        ).strip()

    if not case_number:
        print("❌ Error: Case number is required")
        return 1

    # Create .env file
    env_file = data_dir / ".env"
    with open(env_file, "w") as f:
        f.write(f"USCIS_CASE_NUMBER={case_number}\n")
        f.write("# Optional: Add Telegram settings here\n")
        f.write("# TELEGRAM_BOT_TOKEN=your_token\n")
        f.write("# TELEGRAM_CHAT_ID=your_chat_id\n")

    print(f"✅ Configuration saved to {env_file}")
    print(f"   Case Number: {case_number}")
    print(f"\n📋 Next steps:")
    print(f"   1. Run 'openclaw uscis-start' to start the service")
    print(f"   2. Run 'openclaw uscis-check' to test")
    print(f"   3. Run 'openclaw uscis-schedule' for daily checks")

    return 0


def cmd_start():
    """Start USCIS monitoring service"""
    print("🚀 Starting USCIS monitoring service...")

    data_dir = ensure_data_dir()
    if not (data_dir / "docker-compose.yml").exists():
        print("❌ Error: Not configured. Run 'openclaw uscis-setup' first")
        return 1

    os.chdir(data_dir)
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    print("✅ Service started!")
    print("   FlareSolverr is running on http://localhost:8191")
    return 0


def cmd_stop():
    """Stop USCIS monitoring service"""
    print("🛑 Stopping USCIS monitoring service...")

    data_dir = ensure_data_dir()
    if not (data_dir / "docker-compose.yml").exists():
        print("❌ Error: Not configured")
        return 1

    os.chdir(data_dir)
    subprocess.run(["docker-compose", "down"], check=True)
    print("✅ Service stopped")
    return 0


def cmd_check():
    """Run a one-time USCIS case status check"""
    print("🔍 Checking USCIS case status...")

    data_dir = ensure_data_dir()
    if not (data_dir / "docker-compose.yml").exists():
        print("❌ Error: Not configured. Run 'openclaw uscis-setup' first")
        return 1

    os.chdir(data_dir)

    # Check if service is running
    result = subprocess.run(
        ["docker-compose", "ps", "-q", "flaresolverr"], capture_output=True, text=True
    )

    if not result.stdout.strip():
        print("⚠️  Starting FlareSolverr service first...")
        subprocess.run(["docker-compose", "up", "-d", "flaresolverr"], check=True)
        import time

        time.sleep(5)

    # Run checker
    subprocess.run(["docker-compose", "up", "uscis-checker"])
    return 0


def cmd_schedule():
    """Set up daily automated checks"""
    print("📅 Setting up daily automated checks...")

    data_dir = ensure_data_dir()
    if not (data_dir / "install-cron.sh").exists():
        print("❌ Error: Not configured. Run 'openclaw uscis-setup' first")
        return 1

    os.chdir(data_dir)
    subprocess.run(["bash", "install-cron.sh"], check=True)
    return 0


def cmd_status():
    """View current USCIS case status"""
    data_dir = ensure_data_dir()
    status_file = data_dir / "data" / "status.json"

    if not status_file.exists():
        print("ℹ️  No status found. Run 'openclaw uscis-check' first")
        return 0

    with open(status_file) as f:
        data = json.load(f)

    print("📊 Current USCIS Case Status:")
    print(f"   Case: {data.get('case_number', 'Unknown')}")
    print(f"   Status: {data.get('status', 'Unknown')}")
    print(f"   Last Check: {data.get('timestamp', 'Unknown')}")
    if data.get("description"):
        print(f"   Description: {data['description'][:100]}...")

    return 0


def cmd_logs():
    """View USCIS checker logs"""
    data_dir = ensure_data_dir()
    os.chdir(data_dir)
    subprocess.run(["docker-compose", "logs", "--tail", "50"])
    return 0


def main():
    """Main entry point for OpenClaw skill"""
    if len(sys.argv) < 2:
        print("USCIS Case Checker - OpenClaw Skill")
        print("\nAvailable commands:")
        print("  uscis-setup [case-number]  - Configure the checker")
        print("  uscis-check               - Run status check")
        print("  uscis-start               - Start monitoring service")
        print("  uscis-stop                - Stop monitoring service")
        print("  uscis-schedule            - Set up daily checks")
        print("  uscis-status              - View current status")
        print("  uscis-logs                - View logs")
        return 0

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "uscis-setup": cmd_setup,
        "uscis-check": cmd_check,
        "uscis-start": cmd_start,
        "uscis-stop": cmd_stop,
        "uscis-schedule": cmd_schedule,
        "uscis-status": cmd_status,
        "uscis-logs": cmd_logs,
    }

    if command in commands:
        try:
            return commands[command](*args)
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    else:
        print(f"❌ Unknown command: {command}")
        print(f"Run 'openclaw {SKILL_NAME}' for available commands")
        return 1


if __name__ == "__main__":
    sys.exit(main())

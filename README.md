# USCIS Case Checker

[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)

An automated USCIS case status checker with Cloudflare bypass, Telegram notifications, and Docker deployment. Never miss an update on your immigration case!

## 🚀 Installation Options

### Option 1: OpenClaw Skill (Recommended)

If you use [OpenClaw](https://github.com/openclaw/openclaw), install with one command:

```bash
openclaw skill add uscis-case-checker
openclaw uscis-setup IOE1234567890
```

[Learn more about OpenClaw integration](#openclaw-skill)

### Option 2: Docker (Traditional)

Follow the [Quick Start](#quick-start) guide below for Docker installation.

## Features

- 🔐 **Cloudflare Bypass**: Uses [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) to automatically solve Cloudflare challenges
- 🐳 **Docker Deployment**: Easy setup with Docker Compose
- 📱 **Telegram Notifications**: Get instant alerts on your phone when your case status changes
- 📊 **Status Tracking**: Automatically saves and compares status history
- ⏰ **Scheduled Checks**: Run daily via cron jobs
- 🔒 **Privacy First**: All data stays on your own server

## Supported Case Types

- I-129 (Petition for a Nonimmigrant Worker)
- I-130 (Petition for Alien Relative)
- I-485 (Application to Register Permanent Residence)
- I-765 (Application for Employment Authorization)
- I-131 (Application for Travel Document)
- And all other USCIS case types

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- A VPS or server (can run on Raspberry Pi, home server, or cloud VPS)
- (Optional) Telegram bot for notifications

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/uscis-case-checker.git
cd uscis-case-checker
```

2. **Configure your case number:**
```bash
cp .env.example .env
# Edit .env with your details
```

3. **Start the services:**
```bash
docker-compose up -d
```

4. **Test the check:**
```bash
docker-compose up uscis-checker
```

5. **Set up daily cron job:**
```bash
./install-cron.sh
```

## Configuration

Create a `.env` file with your settings:

```bash
# Required
USCIS_CASE_NUMBER=IOE1234567890

# Optional - for Telegram notifications
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### Getting Telegram Credentials

1. **Create a bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command
   - Save the bot token

2. **Get your chat ID:**
   - Message [@userinfobot](https://t.me/userinfobot)
   - It will reply with your chat ID

3. **Start a chat with your bot:**
   - Search for your bot by username
   - Send `/start` message

## Usage

### Manual Check

Run a one-time check:
```bash
docker-compose up uscis-checker
```

### Scheduled Checks

The `install-cron.sh` script sets up a daily check at 9 AM. To customize:

```bash
# Edit your crontab
crontab -e

# Example: Check every 6 hours
0 */6 * * * cd /path/to/uscis-case-checker && docker-compose up uscis-checker --abort-on-container-exit
```

### Viewing Results

Status is saved to `data/status.json`:
```json
{
  "timestamp": "2025-02-16T23:03:45",
  "case_number": "IOE1234567890",
  "status": "Case Is Still Being Processed By USCIS",
  "description": "As of July 1, 2025, your Form I-129..."
}
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  USCIS Website  │────▶│   FlareSolverr   │────▶│  Case Checker   │
│  (Cloudflare)   │     │  (Bypass Proxy)  │     │   (Playwright)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                                                   ┌──────────────────┐
                                                   │  Telegram Bot    │
                                                   │  (Notifications) │
                                                   └──────────────────┘
```

**How it works:**
1. FlareSolverr handles Cloudflare challenges using a real browser
2. The checker receives cookies and uses Playwright to interact with USCIS
3. Status is extracted from the page and saved
4. If status changed, a Telegram notification is sent

## Troubleshooting

### FlareSolverr not responding
```bash
docker-compose logs flaresolverr
curl http://localhost:8191  # Should return status
```

### Case not found
- Verify your receipt number format (e.g., `IOE1234567890`)
- Check that the case exists on the [official USCIS website](https://egov.uscis.gov/)

### Telegram not working
- Verify bot token and chat ID
- Ensure you started a chat with your bot
- Check bot permissions

### Docker issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Development

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set environment variables
export USCIS_CASE_NUMBER=IOE1234567890

# Run checker
python src/uscis_checker.py
```

### Project Structure

```
.
├── src/
│   └── uscis_checker.py      # Main checker script
├── openclaw-skill/            # OpenClaw skill files
│   ├── skill.json            # Skill configuration
│   └── skill.py              # Skill implementation
├── data/                      # Status storage (created on first run)
├── .env.example              # Configuration template
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Container definition
├── install-cron.sh           # Cron installer
├── requirements.txt          # Python dependencies
├── LICENSE                   # MIT License
├── CONTRIBUTING.md           # Contribution guidelines
└── README.md                 # This file
```

## OpenClaw Skill

This repository includes an [OpenClaw](https://github.com/openclaw/openclaw) skill for easy management via command line.

### Installation

```bash
openclaw skill add uscis-case-checker
```

### Available Commands

| Command | Description |
|---------|-------------|
| `uscis-setup [case-number]` | Configure the checker with your case number |
| `uscis-start` | Start the FlareSolverr monitoring service |
| `uscis-stop` | Stop the monitoring service |
| `uscis-check` | Run a one-time status check |
| `uscis-schedule` | Set up daily automated checks via cron |
| `uscis-status` | View your current case status |
| `uscis-logs` | View recent logs |

### Quick Example

```bash
# Setup your case
openclaw uscis-setup IOE1234567890

# Start the service
openclaw uscis-start

# Run a check
openclaw uscis-check

# Schedule daily checks
openclaw uscis-schedule
```

The skill is located in the `openclaw-skill/` directory and can also be installed manually.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by USCIS. Use at your own risk. Always verify case status on the [official USCIS website](https://egov.uscis.gov/).

## Acknowledgments

- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) - Cloudflare bypass proxy
- [Playwright](https://playwright.dev/) - Browser automation
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Chrome stealth driver

## Support

- 🐛 [Open an Issue](https://github.com/yourusername/uscis-case-checker/issues)
- 💡 [Request a Feature](https://github.com/yourusername/uscis-case-checker/issues)
- ⭐ Star this repo if you find it useful!

---

Made with ❤️ for the immigration community

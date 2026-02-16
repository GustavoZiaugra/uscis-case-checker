# USCIS Case Checker

**Automated USCIS case status monitoring with Cloudflare bypass and Telegram notifications.**

Perfect for tracking your immigration case status without manually checking the USCIS website every day!

## 🚀 Features

- ✅ Automatic Cloudflare bypass
- 📱 Telegram notifications when status changes  
- 🐳 Easy Docker deployment
- ⏰ Daily automated checks
- 🔒 Privacy-first (self-hosted)

## 📋 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/uscis-case-checker.git
cd uscis-case-checker

# Configure
cp .env.example .env
# Edit .env with your case number

# Start services
docker-compose up -d

# Test
docker-compose up uscis-checker

# Setup daily checks
./install-cron.sh
```

See [README.md](README.md) for full documentation.

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

⭐ Star this repo if it helps you!

FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir aiohttp playwright

# Ensure Playwright browsers are installed
RUN playwright install chromium

# Copy the script from src directory
COPY src/uscis_checker.py .

CMD ["python", "uscis_checker.py"]

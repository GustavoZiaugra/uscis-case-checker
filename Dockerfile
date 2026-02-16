FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /app

# Install aiohttp for HTTP requests
RUN pip install --no-cache-dir aiohttp

# Copy the script
COPY src/uscis_checker.py .

CMD ["python", "uscis_checker.py"]

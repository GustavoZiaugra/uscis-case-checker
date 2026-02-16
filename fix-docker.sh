#!/bin/bash
# Fix script for USCIS Case Checker Docker build issues

echo "=== USCIS Case Checker - Docker Fix ==="
echo ""

cd ~/uscis-case-checker

echo "1. Pulling latest changes..."
git pull origin main

echo ""
echo "2. Stopping and removing all containers..."
docker-compose down --remove-orphans

echo ""
echo "3. Removing old images..."
docker rmi uscis-case-checker-uscis-checker:latest 2>/dev/null || true
docker rmi mcr.microsoft.com/playwright/python:v1.58.0-jammy 2>/dev/null || true

echo ""
echo "4. Cleaning Docker build cache..."
docker system prune -f

echo ""
echo "5. Building without cache..."
docker-compose build --no-cache uscis-checker

echo ""
echo "6. Starting FlareSolverr..."
docker-compose up -d flaresolverr

echo ""
echo "7. Waiting 15 seconds for FlareSolverr to initialize..."
sleep 15

echo ""
echo "8. Testing the checker..."
docker-compose up uscis-checker

echo ""
echo "=== Done ==="

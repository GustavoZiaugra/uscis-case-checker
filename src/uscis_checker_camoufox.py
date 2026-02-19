#!/usr/bin/env python3
"""
USCIS Case Status Checker with Camoufox (Cloudflare bypass)

Uses Camoufox anti-detect browser to bypass Cloudflare protection.
- Camoufox: https://github.com/daijro/camoufox
- Telegram notifications
- Status change tracking
- Docker deployment

Usage:
    python uscis_checker_camoufox.py

Environment Variables:
    USCIS_CASE_NUMBER: Your USCIS receipt number (required)
    TELEGRAM_BOT_TOKEN: Telegram bot token (optional)
    TELEGRAM_CHAT_ID: Telegram chat ID (optional)
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import aiohttp
from camoufox.async_api import AsyncCamoufox

# Configuration
CASE_NUMBER = os.environ.get("USCIS_CASE_NUMBER", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

STATE_FILE = (
    Path("/app/data/status.json")
    if Path("/app/data").exists()
    else Path.home() / ".uscis_status.json"
)


async def send_telegram_notification(message: str) -> bool:
    """
    Send notification message to Telegram.

    Args:
        message: The message to send (supports HTML formatting)

    Returns:
        True if sent successfully, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[{datetime.now()}] Telegram not configured")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print(f"[{datetime.now()}] Telegram notification sent")
                    return True
                else:
                    print(f"[{datetime.now()}] Telegram error: {response.status}")
                    return False
    except Exception as e:
        print(f"[{datetime.now()}] Telegram error: {e}")
        return False


async def extract_status_from_page(page) -> Dict[str, str]:
    """
    Extract status information from the USCIS status page.

    Args:
        page: Camoufox/Playwright page object

    Returns:
        Dictionary with 'status' and 'description' keys
    """
    # Try to find status heading (usually h2 on results page)
    status_text = await page.evaluate("""() => {
        const selectors = ['h2', 'h3', '[class*="status"]', '[class*="Status"]'];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (const el of elements) {
                const text = el.textContent.trim();
                if (text && text.length > 10 && text.length < 200 && 
                    (text.toLowerCase().includes('case') || 
                     text.toLowerCase().includes('processed') ||
                     text.toLowerCase().includes('approved') ||
                     text.toLowerCase().includes('pending') ||
                     text.toLowerCase().includes('received'))) {
                    return text;
                }
            }
        }
        return "Unknown";
    }""")

    # Extract description paragraph
    description = await page.evaluate("""() => {
        const paragraphs = document.querySelectorAll('p');
        for (const p of paragraphs) {
            const text = p.textContent.trim();
            if (text.length > 50 && text.length < 500 && 
                (text.includes('Receipt Number') || 
                 text.includes('Form I-') ||
                 text.includes('processed'))) {
                return text;
            }
        }
        for (const p of paragraphs) {
            const text = p.textContent.trim();
            if (text.length > 30 && text.length < 500) {
                return text;
            }
        }
        return "";
    }""")

    return {
        "status": status_text[:200] if status_text else "Unknown",
        "description": description[:500] if description else "",
    }


async def check_case_status() -> Dict[str, Any]:
    """
    Main function to check USCIS case status using Camoufox.

    Uses Camoufox to bypass Cloudflare protection and extract status.

    Returns:
        Dictionary with case status information

    Raises:
        Exception: If the check fails
    """
    print(
        f"[{datetime.now()}] Starting USCIS check with Camoufox for case: {CASE_NUMBER}"
    )

    # Use Camoufox to bypass Cloudflare
    print(f"[{datetime.now()}] Launching Camoufox browser...")

    async with AsyncCamoufox() as browser:
        page = await browser.new_page()

        try:
            # Navigate to landing page
            print(f"[{datetime.now()}] Navigating to USCIS...")
            await page.goto(
                "https://egov.uscis.gov/casestatus/landing.do", timeout=60000
            )
            await asyncio.sleep(3)

            # Fill form
            print(f"[{datetime.now()}] Filling form with case number...")

            selectors = [
                'input[name="appReceiptNum"]',
                'input[id*="receipt"]',
                'input[placeholder*="receipt" i]',
                'input[type="text"]',
            ]

            input_field = None
            for selector in selectors:
                try:
                    input_field = await page.wait_for_selector(selector, timeout=5000)
                    if input_field:
                        print(f"[{datetime.now()}] Found input field: {selector}")
                        break
                except:
                    continue

            if not input_field:
                # Try to save debug screenshot to multiple possible locations
                debug_paths = [
                    "/app/data/debug_landing.png",
                    "./data/debug_landing.png",
                    "/tmp/debug_landing.png",
                ]
                for path in debug_paths:
                    try:
                        await page.screenshot(path=path)
                        break
                    except:
                        continue
                raise Exception("Could not find receipt number input field")

            await input_field.fill("")
            await input_field.fill(CASE_NUMBER)

            # Submit form
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Check")',
                "button",
            ]

            submit_btn = None
            for selector in submit_selectors:
                try:
                    submit_btn = await page.wait_for_selector(selector, timeout=3000)
                    if submit_btn:
                        print(f"[{datetime.now()}] Found submit button: {selector}")
                        break
                except:
                    continue

            if not submit_btn:
                raise Exception("Could not find submit button")

            print(f"[{datetime.now()}] Submitting form...")
            await submit_btn.click()

            await page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(3)

            # Try to save screenshot to multiple possible locations
            screenshot_paths = [
                "/app/data/status_page.png",
                "./data/status_page.png",
                "/tmp/status_page.png",
            ]
            for path in screenshot_paths:
                try:
                    await page.screenshot(path=path)
                    break
                except:
                    continue

            # Extract status
            print(f"[{datetime.now()}] Extracting status...")
            status_info = await extract_status_from_page(page)

            result = {
                "timestamp": datetime.now().isoformat(),
                "case_number": CASE_NUMBER,
                **status_info,
            }

            print(f"[{datetime.now()}] Status found: {result['status']}")

        except Exception as e:
            # Try to save error screenshot to multiple possible locations
            error_paths = ["/app/data/error.png", "./data/error.png", "/tmp/error.png"]
            for path in error_paths:
                try:
                    await page.screenshot(path=path)
                    break
                except:
                    continue
            raise

    # Check for status changes
    previous = load_previous_status()
    status_changed = previous and previous.get("status") != result["status"]

    # Send notification
    emoji = "🎉" if status_changed else "📋"
    change_text = "<b>STATUS CHANGED!</b>\n\n" if status_changed else ""

    message = f"""{emoji} <b>USCIS Case Status</b>

{change_text}<b>Case:</b> <code>{result["case_number"]}</code>
<b>Status:</b> {result["status"]}
<b>Time:</b> {result["timestamp"][:19].replace("T", " ")}

{result.get("description", "")[:300]}"""

    await send_telegram_notification(message)

    save_status(result)
    return result


def load_previous_status() -> Optional[Dict]:
    """Load the previously saved status from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None


def save_status(status: Dict[str, Any]) -> None:
    """Save the current status to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(status, f, indent=2)


def main():
    """Main entry point."""
    if not CASE_NUMBER:
        print("Error: USCIS_CASE_NUMBER environment variable is required")
        print("Example: export USCIS_CASE_NUMBER=MSC1234567890")
        sys.exit(1)

    print(f"[{datetime.now()}] Starting USCIS check for case: {CASE_NUMBER}")

    try:
        result = asyncio.run(check_case_status())
        print(f"\n✓ Check completed successfully!")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Case: {result['case_number']}")
        print(f"Status: {result['status']}")
        if result.get("description"):
            print(f"Description: {result['description'][:100]}...")
        return 0
    except Exception as e:
        print(f"\n✗ Check failed: {e}")

        error_message = f"""❌ <b>USCIS Check Failed</b>

<b>Case:</b> <code>{CASE_NUMBER}</code>
<b>Time:</b> {datetime.now().isoformat()[:19].replace("T", " ")}
<b>Error:</b> {str(e)[:200]}"""
        asyncio.run(send_telegram_notification(error_message))

        return 1


if __name__ == "__main__":
    sys.exit(main())

import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
USER_DATA_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default") # Adjust for Mac
if not os.path.exists(USER_DATA_DIR):
    USER_DATA_DIR = "./user_data" # Fallback to local if default not found

DATA_DIR = "/Users/satvikjain/Downloads/PM/data"

async def handle_response(response):
    """Intercepts and saves JSON responses from career portals."""
    if "json" in response.headers.get("content-type", ""):
        try:
            url = response.url
            # Filter for job-related keywords in URL to avoid noise
            if any(k in url.lower() for k in ["jobs", "search", "career", "postings"]):
                data = await response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"response_{timestamp}_{os.path.basename(url)[:30]}.json"
                filepath = os.path.join(DATA_DIR, filename)
                
                with open(filepath, "w") as f:
                    json.dump({"url": url, "data": data}, f, indent=4)
                print(f"[Captured] {url} -> {filename}")
        except Exception as e:
            pass # Silent fail for non-JSON or parsing errors

async def run_scraper(target_url):
    async with async_playwright() as p:
        # Launch persistent context to use existing cookies/fingerprints
        # Note: Chromium must be installed via 'playwright install'
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # Must be headful for hybrid approach
            args=["--disable-blink-features=AutomationControlled"] # Basic stealth
        )
        
        page = await context.new_page()
        page.on("response", handle_response)
        
        print(f"[*] Navigating to {target_url}...")
        await page.goto(target_url)
        
        print("\n[HYBRID MODE ACTIVE]")
        print("1. Perform manual actions (Login, Solve CAPTCHA, Search parameters).")
        print("2. Navigate through results manually or let the script assist.")
        print("3. Type 'quit' in this terminal to stop.")
        
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "Scraper Command (or press Enter to keep sniffing): ")
            if cmd.lower() == "quit":
                break
            elif cmd.lower() == "scroll":
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
        await context.close()

if __name__ == "__main__":
    # Example target: Microsoft Careers
    target = "https://careers.microsoft.com/v2/global/en/search.html?q=Product%20Manager"
    asyncio.run(run_scraper(target))

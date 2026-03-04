import asyncio
import json
import os
import sys
import argparse
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
USER_DATA_DIR = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
if not os.path.exists(USER_DATA_DIR):
    USER_DATA_DIR = "./user_data"

DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
BEHAVIOR_FILE = os.path.join(DATA_DIR, "behavior.json")

class ScraperObserver:
    def __init__(self):
        self.interactions = []
        self.api_responses = []
        self.patterns = {}

    async def log_click(self, selector, url):
        timestamp = datetime.now().isoformat()
        print(f"[Observer] Click detected on: {selector}")
        self.interactions.append({
            "type": "click",
            "selector": selector,
            "url": url,
            "timestamp": timestamp
        })

    async def log_response(self, url, content_type):
        timestamp = datetime.now().isoformat()
        self.api_responses.append({
            "url": url,
            "content_type": content_type,
            "timestamp": timestamp
        })

    def analyze_patterns(self):
        """Correlates clicks with subsequent API calls."""
        print("[*] Analyzing patterns...")
        for i, interaction in enumerate(self.interactions):
            # Find API calls that happened shortly after the click
            follow_up_apis = [
                resp for resp in self.api_responses 
                if resp["timestamp"] > interaction["timestamp"]
            ][:3] # Take next 3 responses
            
            if follow_up_apis:
                self.patterns[interaction["selector"]] = {
                    "trigger": interaction["type"],
                    "apis": follow_up_apis
                }
        
        with open(BEHAVIOR_FILE, "w") as f:
            json.dump(self.patterns, f, indent=4)
        print(f"[+] Patterns saved to {BEHAVIOR_FILE}")
        self.generate_mermaid()

    def generate_mermaid(self):
        mermaid = "graph TD\n"
        mermaid += "    Start[User Search] --> Browse[Job Results]\n"
        for selector, data in self.patterns.items():
            clean_sel = selector.replace('"', "'")
            mermaid += f'    Browse -- "Click {clean_sel}" --> API["{data["apis"][0]["url"][:50]}..."]\n'
            mermaid += f'    API --> Browse\n'
        
        mermaid_file = os.path.join(DATA_DIR, "loop_diagram.md")
        with open(mermaid_file, "w") as f:
            f.write(f"```mermaid\n{mermaid}\n```")
        print(f"[+] Mermaid diagram generated at {mermaid_file}")

observer = ScraperObserver()

async def handle_response(response):
    """Intercepts and saves JSON responses from career portals."""
    content_type = response.headers.get("content-type", "")
    if response.status in [403, 429]:
        print(f"\a[!!!] Security hurdle detected ({response.status})! Please solve CAPTCHA/Verify in the browser.")
    
    if "json" in content_type:
        try:
            url = response.url
            if any(k in url.lower() for k in ["jobs", "search", "career", "postings", "api"]):
                data = await response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"response_{timestamp}_{os.path.basename(url)[:30]}.json"
                filepath = os.path.join(DATA_DIR, filename)
                
                with open(filepath, "w") as f:
                    json.dump({"url": url, "data": data}, f, indent=4)
                print(f"[Captured] {url}")
                await observer.log_response(url, content_type)
        except Exception:
            pass

async def inject_observer(page):
    """Injects JavaScript to monitor clicks in real-time."""
    await page.expose_function("notifyClick", lambda selector, url: asyncio.create_task(observer.log_click(selector, url)))
    await page.add_init_script("""
        document.addEventListener('click', (e) => {
            const target = e.target.closest('button, a, [role="button"]');
            if (target) {
                const selector = target.id ? `#${target.id}` : (target.className ? `.${target.className.split(' ').join('.')}` : target.tagName);
                window.notifyClick(selector, window.location.href);
            }
        }, true);
    """)

async def run_scraper(target_url, learn_mode=False):
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = await context.new_page()
        page.on("response", handle_response)
        
        if learn_mode:
            print("[LEARNING MODE] Observing your actions...")
            await inject_observer(page)
        
        print(f"[*] Navigating to {target_url}...")
        await page.goto(target_url)
        
        print("\n[HYBRID MODE ACTIVE]")
        if learn_mode:
            print("Action Required: Perform the search and click 'Next' or 'Load More' 2-3 times.")
        
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "Command (scroll/save/quit): ")
            if cmd.lower() == "quit":
                if learn_mode:
                    observer.analyze_patterns()
                break
            elif cmd.lower() == "scroll":
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            elif cmd.lower() == "save" and learn_mode:
                observer.analyze_patterns()
            
        await context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://careers.microsoft.com/v2/global/en/search.html?q=Product%20Manager")
    parser.add_argument("--learn", action="store_true", help="Enable learning mode")
    args = parser.parse_args()
    
    os.makedirs(DATA_DIR, exist_ok=True)
    asyncio.run(run_scraper(args.url, learn_mode=args.learn))

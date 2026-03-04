import asyncio
import json
import os
import argparse
from datetime import datetime
from playwright.async_api import async_playwright

# Configuration
USER_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "scraper_profile")
os.makedirs(USER_DATA_DIR, exist_ok=True)

DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
os.makedirs(DATA_DIR, exist_ok=True)

class DiscoveryObserver:
    def __init__(self, company_name):
        self.company_name = company_name
        self.interactions = []
        self.api_responses = []
        self.patterns = {}
        self.behavior_file = os.path.join(DATA_DIR, f"{company_name}_behavior.json")

    async def log_click(self, selector, url):
        timestamp = datetime.now().isoformat()
        print(f"[Discovery] Click detected: {selector}")
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
        print(f"[*] Analyzing patterns for {self.company_name}...")
        for i, interaction in enumerate(self.interactions):
            follow_up_apis = [
                resp for resp in self.api_responses 
                if resp["timestamp"] > interaction["timestamp"]
            ][:3]
            
            if follow_up_apis:
                self.patterns[interaction["selector"]] = {
                    "trigger": interaction["type"],
                    "apis": follow_up_apis
                }
        
        with open(self.behavior_file, "w") as f:
            json.dump(self.patterns, f, indent=4)
        print(f"[+] Behavior saved to {self.behavior_file}")
        self.generate_mermaid()

    def generate_mermaid(self):
        mermaid = "graph TD\n"
        mermaid += "    Start[Start Search] --> Browse[Results Page]\n"
        for selector, data in self.patterns.items():
            clean_sel = selector.replace('"', "'")
            mermaid += f'    Browse -- "Click {clean_sel}" --> API["{data["apis"][0]["url"][:50]}..."]\n'
            mermaid += f'    API --> Browse\n'
        
        mermaid_file = os.path.join(DATA_DIR, f"{self.company_name}_loop.md")
        with open(mermaid_file, "w") as f:
            f.write(f"```mermaid\n{mermaid}\n```")
        print(f"[+] Mermaid diagram at {mermaid_file}")

async def handle_response(response, observer):
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        try:
            url = response.url
            if any(k in url.lower() for k in ["jobs", "search", "career", "postings", "api"]):
                data = await response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                filename = f"discovery_{observer.company_name}_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, "w") as f:
                    json.dump({"url": url, "data": data}, f, indent=4)
                await observer.log_response(url, content_type)
        except: pass

async def inject_observer(page, observer):
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

async def run_discovery(company, url):
    observer = DiscoveryObserver(company)
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()
        page.on("response", lambda r: handle_response(r, observer))
        await inject_observer(page, observer)
        
        print(f"[*] Navigating to {url}...")
        await page.goto(url)
        print("\n[DISCOVERY MODE ACTIVE]")
        print("1. Perform the search manually.")
        print("2. Click regular job cards and 'Next' page buttons.")
        print("3. Type 'save' here when done.")

        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "Command (save/quit): ")
            if cmd.lower() in ["save", "quit"]:
                observer.analyze_patterns()
                break
        await context.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    asyncio.run(run_discovery(args.company, args.url))

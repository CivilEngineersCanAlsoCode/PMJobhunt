import asyncio
import json
import os
import csv
import re
from datetime import datetime
from playwright.async_api import async_playwright

# -----------------------------------------------------------------------------
# KNOWLEDGE BASE REFERENCE: research documents/Scraping_Career_Portals_Analysis.md
# SYSTEM IDENTIFIED: Eightfold.ai (Microsoft flavor)
# STRATEGY: 
#   1. Pre-scroll to trigger lazy loading.
#   2. Use cardContainer/card-F1ebU classes for high-fidelity selection.
#   3. Handle 'detached DOM' errors during Virtual Scroll iteration.
# -----------------------------------------------------------------------------

# Configuration
USER_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "scraper_profile")
DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
OUTPUT_CSV = os.path.join(DATA_DIR, "microsoft_pm_jobs.csv")

# Selectors from Discovery (Refined for Eightfold/Microsoft)
NEXT_BUTTON_SELECTOR = ".pagination-module_pagination-button__aTecY.pagination-module_pagination-next__OHCf9, button[aria-label*='Next'], .pagination-next, [data-automation-id='next-button']"
JOB_CARD_SELECTOR = '.card-F1ebU, .cardContainer-GcY1a, li[id^="job-card-"], .job-card, [role="listitem"]'
KB_FILE = "/Users/satvikjain/Downloads/PM/research documents/Scraping_Career_Portals_Analysis.md"

def log_learning(company, error, solution):
    """Appends a new learning case to the Scraping Analysis Knowledge Base."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n### [{company}] Learning Case ({timestamp})\n\n"
    entry += f"- **Error**: {error}\n"
    entry += f"- **Solution**: {solution}\n"
    
    try:
        with open(KB_FILE, "a") as f:
            f.write(entry)
        print(f"  [Knowledge Base] Logged new learning for {company}")
    except Exception as e:
        print(f"  [!] Failed to update Knowledge Base: {e}")

async def handle_response(response):
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        try:
            url = response.url
            if "position_details" in url:
                data = await response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                filename = f"microsoft_detail_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                with copy_open(filepath, "w") as f:
                    json.dump({"url": url, "data": data}, f, indent=4)
                print(f"  [Captured] {url}")
        except: pass

def copy_open(path, mode):
    # Helper to ensure data dir exists
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, mode)

def parse_experience(jd_html):
    match = re.search(r"(\d+)\+?\s*years?\s*(?:of\s*)?experience", jd_html, re.IGNORECASE)
    if match: return f"{match.group(1)}+ years"
    return "Not specified"

def export_to_csv():
    import glob
    files = glob.glob(os.path.join(DATA_DIR, "microsoft_detail_*.json"))
    unique_jobs = {}
    for f in files:
        try:
            with open(f, 'r') as j:
                content = json.load(j)
                job_data = content.get('data', {}).get('data', {})
                job_id = job_data.get('displayJobId')
                if job_id and job_id not in unique_jobs:
                    jd_raw = job_data.get('jobDescription', '')
                    # Clean tags to match manual_capture style
                    jd_clean = jd_raw.replace('<br/>', '\n').replace('<br>', '\n').strip()
                    unique_jobs[job_id] = {
                        'Job Title': job_data.get('name'),
                        'Job ID': job_id,
                        'Location': job_data.get('location'),
                        'Description': jd_clean,
                        'Apply Link': f"https://apply.careers.microsoft.com{job_data.get('positionUrl', '')}"
                    }
        except Exception as e:
            err_msg = str(e)
            print(f"  [!] Skip {os.path.basename(f)}: {err_msg}")
            log_learning("Microsoft", f"JSON Parsing Error in {os.path.basename(f)}", f"Check if Eightfold schema has changed. Error: {err_msg}")

    if unique_jobs:
        fieldnames = ['Job Title', 'Job ID', 'Location', 'Description', 'Apply Link']
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for jid in sorted(unique_jobs.keys()): writer.writerow(unique_jobs[jid])
        print(f"[+] Exported {len(unique_jobs)} jobs to {OUTPUT_CSV}")

async def run_automation():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()
        page.on("response", handle_response)
        
        print("[*] Launching Microsoft Portal. Please navigate to your search results.")
        await page.goto("https://careers.microsoft.com/v2/global/en/search.html")
        
        print("\n[WAITING FOR TAKEOVER]")
        print("Action: Navigate to results. Once the jobs are listed, type 'start' here.")
        
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "Takeover Command (start/quit): ")
            if cmd.lower() == "start":
                break
            if cmd.lower() == "quit":
                await context.close()
                return

        print("[*] Automation starting...")
        page_num = 1
        while True:
            print(f"[*] Processing Page {page_num}...")
            try:
                # Scroll to trigger lazy loading
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                
                # Wait for any form of job card to appear
                await page.wait_for_selector(JOB_CARD_SELECTOR, timeout=15000)
                cards = await page.query_selector_all(JOB_CARD_SELECTOR)
                print(f"[+] Found {len(cards)} job cards.")
                
                for i, card in enumerate(cards):
                    try:
                        await card.scroll_into_view_if_needed()
                        await card.click()
                        print(f"  [Clicked] {i+1}/{len(cards)}")
                        await asyncio.sleep(2) # Stabilize for API response
                    except Exception as e:
                        print(f"  [!] Skip card {i+1}: {e}")
            except Exception as e:
                err_msg = str(e)
                print(f"[!] Critical Automation Error: {err_msg}")
                log_learning("Microsoft", f"Automation Loop Break: {err_msg}", "Check if JOB_CARD_SELECTOR or pagination button changed.")
                # Optional: log a snippet of HTML for debugging
                html = await page.content()
                with open("/tmp/ms_portal_debug.html", "w") as f: f.write(html)
                break
            
            # Try to paginate
            next_btn = await page.query_selector(NEXT_BUTTON_SELECTOR)
            if next_btn and await next_btn.is_visible() and await next_btn.is_enabled():
                print("[*] Moving to next page...")
                await next_btn.click()
                page_num += 1
                await asyncio.sleep(3)
            else:
                print("[+] End of list or next button hidden.")
                break
        
        print("[*] Extraction complete. Exporting CSV...")
        export_to_csv()
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_automation())

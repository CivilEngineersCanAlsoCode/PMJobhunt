import asyncio
import json
import os
import csv
import re
import glob
from datetime import datetime
from playwright.async_api import async_playwright

# -----------------------------------------------------------------------------
# PASSIVE MANUAL CAPTURE ENGINE
# Purpose: Zero-automation monitoring. Watches user actions and records data.
# -----------------------------------------------------------------------------

# Configuration
USER_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "scraper_profile")
DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
KB_FILE = "/Users/satvikjain/Downloads/PM/research documents/Scraping_Career_Portals_Analysis.md"
os.makedirs(DATA_DIR, exist_ok=True)

async def handle_response(response, company_name):
    """Intercepts JSON responses and saves them if they look like job details."""
    content_type = response.headers.get("content-type", "")
    if "json" in content_type:
        try:
            url = response.url
            # Detectable JSON but maybe not saved yet
            print(f"  [JSON] {url[:80]}...") 
            
            # Generic keywords for job APIs
            if any(k in url.lower() for k in ["detail", "position", "job", "posting", "api", "v1", "v2"]):
                data = await response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                filename = f"manual_{company_name}_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, "w") as f:
                    json.dump({"url": url, "data": data}, f, indent=4)
                print(f"  [Captured] {url}")
        except: pass

def parse_experience(jd_html):
    if not jd_html: return "Not specified"
    match = re.search(r"(\d+)\+?\s*years?\s*(?:of\s*)?experience", str(jd_html), re.IGNORECASE)
    if match: return f"{match.group(1)}+ years"
    return "Not specified"

def universal_export(company_name):
    """Attempts to parse captured JSONs from any schema into a unified CSV."""
    output_csv = os.path.join(DATA_DIR, f"{company_name}_manual_jobs.csv")
    files = glob.glob(os.path.join(DATA_DIR, f"manual_{company_name}_*.json"))
    unique_jobs = {}

    print(f"[*] Processing {len(files)} captured files...")

    for f in files:
        try:
            with open(f, 'r') as j:
                content = json.load(j)
                raw_data = content.get('data', {})
                
                # Normalize raw_data into a list of job objects
                job_list = []
                if isinstance(raw_data, dict):
                    if 'jobs' in raw_data and isinstance(raw_data['jobs'], list):
                        job_list = raw_data['jobs'] # Amazon / Search Results style
                    elif 'data' in raw_data and isinstance(raw_data['data'], dict):
                        job_list = [raw_data['data']] # Microsoft / Detail View style
                    elif 'job' in raw_data:
                        job_list = [raw_data['job']] # Common single-job wrapper
                    else:
                        job_list = [raw_data] # Direct object
                elif isinstance(raw_data, list):
                    job_list = raw_data
                
                for job_data in job_list:
                    if not isinstance(job_data, dict): continue
                    
                    # Search for standard keys
                    title = job_data.get('title') or job_data.get('name') or job_data.get('job_title')
                    job_id = job_data.get('id') or job_data.get('displayJobId') or job_data.get('job_id') or job_data.get('jobId')
                    
                    if title and job_id and job_id not in unique_jobs:
                        jd = job_data.get('description') or job_data.get('jobDescription') or job_data.get('basic_qualifications', '')
                        loc = job_data.get('location') or job_data.get('normalized_location') or "Check JSON"
                        
                        unique_jobs[job_id] = {
                            'Job Title': title,
                            'Job ID': job_id,
                            'Location': loc,
                            'Description': jd.replace('<br/>', '\n').replace('<br>', '\n').strip(),
                            'Apply Link': job_data.get('url') or job_data.get('positionUrl') or job_data.get('url_next_step') or content.get('url')
                        }
        except Exception as e:
            print(f"  [!] Skip {os.path.basename(f)}: {e}")

    if unique_jobs:
        fieldnames = ['Job Title', 'Job ID', 'Location', 'Description', 'Apply Link']
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for jid in sorted(unique_jobs.keys()): writer.writerow(unique_jobs[jid])
        print(f"[+] Exported {len(unique_jobs)} jobs to {output_csv}")
    else:
        print("[!] No unique jobs found to export.")

async def run_manual_capture(company_name):
    async with async_playwright() as p:
        print(f"[*] Launching Manual Capture for {company_name}...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()
        page.on("response", lambda r: handle_response(r, company_name))
        
        print("\n[PASSIVE MODE ACTIVE]")
        print("Action: Navigate to any career portal. Every job you click will be recorded.")
        print("Capture: Simply click job cards to trigger their detail views.")
        print("Note: There is NO automation. You are in full control.")
        
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "\nCommand (stop/quit): ")
            if cmd.lower() in ["stop", "quit"]:
                break

        print("[*] Capture complete. Running Universal Export...")
        universal_export(company_name)
        await context.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True, help="Name of the company being captured")
    args = parser.parse_args()
    asyncio.run(run_manual_capture(args.company))

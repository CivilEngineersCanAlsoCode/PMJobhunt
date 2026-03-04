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

# State for controlled capture
state = {
    "capturing": False
}

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

async def handle_response(response, company_name):
    """Intercepts and captures ALL JSON responses when capturing is ON."""
    if not state["capturing"]:
        return

    url = response.url
    # Filter out common noise
    if any(ignore in url for ignore in [".js", ".css", ".png", ".jpg", ".svg", ".woff", "google-analytics", "telemetry", "doubleclick"]):
        return

    try:
        content_type = response.headers.get("content-type", "").lower()
        
        # Capture if it's JSON or if it's an API-like URL
        is_json = "json" in content_type
        is_api = any(k in url.lower() for k in ["api/", "graphql", "v1/", "v2/", "get", "results"])
        
        if is_json or is_api:
            try:
                data = await response.json()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")
                filename = f"manual_{company_name}_{timestamp}.json"
                filepath = os.path.join(DATA_DIR, filename)
                with open(filepath, "w") as f:
                    json.dump({"url": url, "data": data}, f, indent=4)
                print(f"  [Captured API] {url[:100]}...")
            except:
                # If json parsing fails but it was an API URL, we could capture as text
                # but for jobs usually JSON is the gold standard.
                pass
    except: pass

def parse_experience(jd_html):
    if not jd_html: return "Not specified"
    match = re.search(r"(\d+)\+?\s*years?\s*(?:of\s*)?experience", str(jd_html), re.IGNORECASE)
    if match: return f"{match.group(1)}+ years"
    return "Not specified"

def clean_description(jd):
    if not jd: return ""
    return jd.replace('<br/>', '\n').replace('<br>', '\n').replace('<div>', '').replace('</div>', '').replace('<p>', '').replace('</p>', '\n').strip()

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
                        # Nested Microsoft detail
                        inner_data = raw_data.get('data', {})
                        if isinstance(inner_data, dict) and (inner_data.get('id') or inner_data.get('name')):
                            job_list = [inner_data]
                        else:
                            job_list = [raw_data['data']]
                    elif 'job' in raw_data and isinstance(raw_data['job'], dict):
                        job_list = [raw_data['job']]
                    elif 'jobs' in raw_data and isinstance(raw_data['jobs'], dict):
                         job_list = [raw_data['jobs']]
                    else:
                        job_list = [raw_data] # Direct object
                elif isinstance(raw_data, list):
                    job_list = raw_data
                
                for job_data in job_list:
                    if not isinstance(job_data, dict): continue
                    
                    # Search for standard keys
                    title = job_data.get('title') or job_data.get('name') or job_data.get('job_title')
                    job_id = job_data.get('id') or job_data.get('displayJobId') or job_data.get('job_id') or job_data.get('jobId')
                    
                    if title and job_id and str(job_id) not in unique_jobs:
                        jd = job_data.get('description') or job_data.get('jobDescription') or job_data.get('basic_qualifications', '') or job_data.get('responsibilities', '')
                        if not jd and 'description' in job_data: jd = job_data['description']
                        
                        loc = job_data.get('location') or job_data.get('normalized_location') or job_data.get('locations')
                        if isinstance(loc, list) and loc: loc = loc[0]
                        if not loc: loc = "Check JSON"
                        
                        unique_jobs[str(job_id)] = {
                            'Job Title': title,
                            'Job ID': job_id,
                            'Location': loc,
                            'Description': clean_description(jd),
                            'Apply Link': job_data.get('url') or job_data.get('positionUrl') or job_data.get('url_next_step') or job_data.get('publicUrl') or content.get('url')
                        }
        except Exception as e:
            err_msg = str(e)
            print(f"  [!] Skip {os.path.basename(f)}: {err_msg}")
            log_learning(company_name, f"JSON Parsing Error in {os.path.basename(f)}", f"Check if schema has changed. Error: {err_msg}")

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
        page.on("response", lambda r: asyncio.ensure_future(handle_response(r, company_name)))
        
        print("\n[CONTROLLED CAPTURE MODE]")
        print("1. Navigate to the job listing page.")
        print("2. Type 'start' to begin recording network traffic.")
        print("3. Click onto job details to capture them.")
        print("4. Type 'stop' to finish and export data.")
        
        while True:
            cmd = await asyncio.get_event_loop().run_in_executor(None, input, "\nCommand (start/stop/quit): ")
            cmd_clean = cmd.lower().strip()
            
            if cmd_clean == "start":
                state["capturing"] = True
                print(">>> CAPTURE STARTED. Interaction recording is ON.")
            elif cmd_clean == "stop":
                state["capturing"] = False
                print(">>> CAPTURE STOPPED. Preparing export...")
                break
            elif cmd_clean == "quit":
                break

        universal_export(company_name)
        await context.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True, help="Name of the company being captured")
    args = parser.parse_args()
    asyncio.run(run_manual_capture(args.company))

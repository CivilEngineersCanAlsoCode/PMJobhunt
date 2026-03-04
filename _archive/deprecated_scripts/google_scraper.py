"""
google_scraper.py - Scrapes Google Careers using direct HTTP GET + HTML Parsing.

Research confirmed: Google embeds all job data directly in raw HTML.
NO browser automation needed. Executes in seconds, zero ban risk.
"""

import requests
import json
import csv
import re
import os

DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
OUTPUT_CSV = os.path.join(DATA_DIR, "Google_manual_jobs.csv")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_google_jobs(query="Product Manager", location="India"):
    """Scrape Google Careers by parsing the AF_initDataCallback data block."""
    search_url = "https://www.google.com/about/careers/applications/jobs/results/"
    params = {"q": query, "location": location}
    
    print(f"[*] Fetching Google Careers: {search_url}")
    response = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
    print(f"[*] HTTP Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"[!] Failed: {response.status_code}")
        return []
    
    html = response.text
    
    # Google embeds job data in AF_initDataCallback({key: 'ds:1', ...}) block
    # Each job is: ["job_id", "title", "apply_url", [null, "description_html", ...], ...]
    idx = html.find("AF_initDataCallback({key: 'ds:1'")
    if idx == -1:
        print("[!] Could not find ds:1 block")
        return []
    
    # Extract the data array from the block
    data_start = html.find("data:", idx) + 5
    # Use a bracket counter to find the matching close bracket
    depth = 0
    end = data_start
    for i, ch in enumerate(html[data_start:], start=data_start):
        if ch == '[': depth += 1
        elif ch == ']': 
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    
    raw_data_str = html[data_start:end]
    
    try:
        job_array = json.loads(raw_data_str)
    except Exception as e:
        print(f"[!] JSON parse error: {e}")
        return []
    
    jobs = []
    # job_array is [[[job1_data], [job2_data], ...], ...]
    job_list = job_array[0] if job_array and isinstance(job_array[0], list) else job_array
    
    for job in job_list:
        if not isinstance(job, list) or len(job) < 3:
            continue
        
        job_id = str(job[0]) if job[0] else ""
        title = job[1] if len(job) > 1 else ""
        apply_url = job[2] if len(job) > 2 else ""
        
        # Description is in index 3: [null, "description_html", ...]
        description = ""
        if len(job) > 3 and isinstance(job[3], list):
            for part in job[3]:
                if isinstance(part, str) and len(part) > 50:
                    description = re.sub('<[^<]+?>', '', part).strip()
                    break
        
        # Location is often in index 4 or 5
        location_val = ""
        for idx_loc in [4, 5, 6]:
            if len(job) > idx_loc and isinstance(job[idx_loc], str) and job[idx_loc]:
                location_val = job[idx_loc]
                break
        
        if title and job_id:
            jobs.append({
                'Job Title': title,
                'Job ID': job_id,
                'Location': location_val or location or "India",
                'Description': description,
                'Apply Link': apply_url
            })
    
    print(f"[*] Extracted {len(jobs)} jobs")
    return jobs

def fetch_job_details(job_url):
    """Fetch full description for a specific Google job."""
    response = requests.get(job_url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        return ""
    
    html = response.text
    
    # Try JSON-LD first
    json_ld_matches = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for match in json_ld_matches:
        try:
            data = json.loads(match)
            if data.get('@type') == 'JobPosting':
                return re.sub('<[^<]+?>', '', data.get('description', '')).strip()
        except:
            pass
    
    # Fall back to HTML parsing
    desc_match = re.search(r'<div[^>]*class="[^"]*gc-job-description[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
    if desc_match:
        return re.sub('<[^<]+?>', '', desc_match.group(1)).strip()
    
    return ""

def save_to_csv(jobs):
    fieldnames = ['Job Title', 'Job ID', 'Location', 'Description', 'Apply Link']
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            writer.writerow(job)
    print(f"[+] Saved {len(jobs)} jobs to {OUTPUT_CSV}")

if __name__ == "__main__":
    jobs = scrape_google_jobs(query="Product Manager", location="India")
    
    if not jobs:
        print("[!] No jobs found. Trying broader search...")
        jobs = scrape_google_jobs(query="Product Manager", location="")
    
    print(f"\n[*] Total jobs found: {len(jobs)}")
    for i, j in enumerate(jobs[:5]):
        print(f"  {i+1}. {j['Job Title']} - {j['Location']}")
    
    if jobs:
        save_to_csv(jobs)
    else:
        print("[!] No jobs found. Google may have changed their HTML structure.")
        print("    Saving raw HTML for inspection...")
        import requests
        r = requests.get("https://www.google.com/about/careers/applications/jobs/results/?q=Product+Manager&location=India", headers=HEADERS)
        raw_path = os.path.join(DATA_DIR, "google_raw.html")
        with open(raw_path, 'w', encoding='utf-8') as f:
            f.write(r.text)
        print(f"    Saved to {raw_path}")

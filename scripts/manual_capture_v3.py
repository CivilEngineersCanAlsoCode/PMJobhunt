"""
manual_capture_v3.py — Universal Passive Capture Engine
========================================================
Three-Tier Architecture (MECE):
  Tier 1 - Network Layer   : Intercepts all JSON/API responses
  Tier 2 - DOM Layer       : Full page HTML snapshot on each navigation
  Tier 3 - Snapshot Layer  : Periodic body snapshot (catches lazy-load & SPAs)

Works for ANY career portal regardless of architecture.
User controls start/stop via terminal commands.
"""

import asyncio
import hashlib
import json
import csv
import re
import os
import glob
from datetime import datetime
from playwright.async_api import async_playwright

# ── Configuration ─────────────────────────────────────────────────────────────
USER_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "scraper_profile")
BASE_DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
KB_FILE = "/Users/satvikjain/Downloads/PM/research documents/Scraping_Career_Portals_Analysis.md"

# Per-session folders
NETWORK_DIR = os.path.join(BASE_DATA_DIR, "raw_network")
DOM_DIR = os.path.join(BASE_DATA_DIR, "raw_dom")
SNAPSHOT_DIR = os.path.join(BASE_DATA_DIR, "raw_snapshots")

for d in [NETWORK_DIR, DOM_DIR, SNAPSHOT_DIR]:
    os.makedirs(d, exist_ok=True)

# Shared state
state = {"capturing": False}

# ── Helpers ───────────────────────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S.%f")

def clean_html(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.replace('&nbsp;', ' ').replace('&amp;', '&').strip()

def log_learning(company, error, solution):
    entry = f"\n### [{company}] Learning Case ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n- **Error**: {error}\n- **Solution**: {solution}\n"
    try:
        with open(KB_FILE, "a") as f: f.write(entry)
    except: pass

# ── TIER 1: Network Layer ─────────────────────────────────────────────────────
NOISE_PATTERNS = [".js", ".css", ".png", ".jpg", ".svg", ".woff", ".ico",
                  "google-analytics", "telemetry", "doubleclick", "gtm",
                  "fonts.googleapis", "collect?v="]

async def handle_response(response, company):
    """Save all JSON/API responses."""
    if not state["capturing"]: return
    url = response.url
    if any(p in url for p in NOISE_PATTERNS): return
    try:
        ct = response.headers.get("content-type", "").lower()
        is_json = "json" in ct
        is_api  = any(k in url.lower() for k in ["api/", "graphql", "v1/", "v2/", "/get", "results", "search", "jobs"])
        if is_json or is_api:
            data = await response.json()
            path = os.path.join(NETWORK_DIR, f"net_{company}_{ts()}.json")
            with open(path, "w") as f:
                json.dump({"url": url, "data": data}, f, indent=2)
            print(f"  [T1-Net] {url[:90]}...")
    except: pass

# ── TIER 2: DOM Layer ─────────────────────────────────────────────────────────
async def handle_navigation(page, company):
    """Save full page HTML after each navigation + network idle."""
    if not state["capturing"]: return
    try:
        await page.wait_for_load_state("networkidle", timeout=6000)
        html = await page.content()
        path = os.path.join(DOM_DIR, f"dom_{company}_{ts()}.html")
        with open(path, "w", encoding="utf-8") as f: f.write(html)
        print(f"  [T2-DOM] Page snapshot saved ({len(html)//1024}KB)")
    except: pass

# ── TIER 3: Periodic Snapshot Layer ──────────────────────────────────────────
async def periodic_snapshot_loop(page, company):
    """Background loop: save body HTML every 2s only when content changes."""
    last_hash = ""
    print("  [T3-Snap] Periodic snapshot loop started")
    while state["capturing"]:
        try:
            html = await page.inner_html("body")
            h = hashlib.md5(html.encode()).hexdigest()
            if h != last_hash:
                path = os.path.join(SNAPSHOT_DIR, f"snap_{company}_{ts()}.html")
                with open(path, "w", encoding="utf-8") as f: f.write(html)
                last_hash = h
                print(f"  [T3-Snap] Content changed, snapshot saved ({len(html)//1024}KB)")
        except: pass
        await asyncio.sleep(2)

# ── UNIVERSAL EXPORT ENGINE ───────────────────────────────────────────────────
def parse_google_html(html, src_url=""):
    """Parse Google's AF_initDataCallback ds:1 block."""
    jobs = []
    idx = html.find("AF_initDataCallback({key: 'ds:1'")
    if idx == -1: return jobs
    data_start = html.find("data:", idx) + 5
    depth, end = 0, data_start
    for i, ch in enumerate(html[data_start:], start=data_start):
        if ch == '[': depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0: end = i + 1; break
    try:
        job_array = json.loads(html[data_start:end])
        job_list = job_array[0] if job_array and isinstance(job_array[0], list) else job_array
        for job in job_list:
            if not isinstance(job, list) or len(job) < 3: continue
            job_id, title, apply_url = str(job[0]), job[1], job[2]
            desc_parts = []
            if len(job) > 3 and isinstance(job[3], list):
                for part in job[3]:
                    if isinstance(part, str) and len(part) > 20:
                        desc_parts.append(clean_html(part))
            loc = ""
            for item in job[3:]:
                if isinstance(item, list):
                    for sub in item:
                        if isinstance(sub, list) and sub and isinstance(sub[0], str):
                            candidate = sub[0]
                            if ',' in candidate and 'projects/' not in candidate and 'http' not in candidate:
                                loc = candidate; break
                    if loc: break
            if title and job_id:
                jobs.append({"Job Title": title, "Job ID": job_id, "Location": loc or "India",
                             "Description": " ".join(desc_parts), "Apply Link": apply_url})
    except: pass
    return jobs

def parse_json_ld(html):
    """Parse JSON-LD structured data (standard web)."""
    jobs = []
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(m)
            items = data.get('itemListElement', []) if data.get('@type') == 'ItemList' else ([data] if data.get('@type') == 'JobPosting' else [])
            for item in items:
                job = item.get('item', item)
                jobs.append({
                    "Job Title": job.get("title", ""),
                    "Job ID": job.get("identifier", {}).get("value", job.get("url", "").split("/")[-1]),
                    "Location": job.get("jobLocation", {}).get("address", {}).get("addressLocality", ""),
                    "Description": clean_html(job.get("description", "")),
                    "Apply Link": job.get("url", "")
                })
        except: pass
    return jobs

def parse_json_response(content, url):
    """Parse a captured JSON network response — try multiple schemas."""
    jobs = []
    data = content.get("data", {})
    raw = content
    
    def extract_from_dict(d):
        if not isinstance(d, dict): return None
        # Microsoft nested: data.data.*
        inner = d.get("data", d)
        if isinstance(inner, dict) and (inner.get("name") or inner.get("title")) and inner.get("id"):
            d = inner
        job_id = d.get("id") or d.get("displayJobId") or d.get("job_id") or d.get("jobId")
        title  = d.get("name") or d.get("title") or d.get("job_title")
        if not (job_id and title): return None
        jd  = d.get("jobDescription") or d.get("description") or d.get("basic_qualifications", "")
        locs = d.get("locations") or d.get("location")
        loc  = (locs[0] if isinstance(locs, list) and locs else locs) or ""
        link = d.get("publicUrl") or d.get("positionUrl") or d.get("url") or d.get("url_next_step") or url
        return {"Job Title": title, "Job ID": str(job_id), "Location": str(loc),
                "Description": clean_html(jd), "Apply Link": link}
    
    # Try top-level single job
    job = extract_from_dict(data if isinstance(data, dict) else raw)
    if job: return [job]
    
    # Try list of jobs
    candidate_list = None
    if isinstance(data, dict):
        candidate_list = data.get("jobs") or data.get("results") or data.get("items")
    if isinstance(data, list):
        candidate_list = data
    if candidate_list:
        for item in (candidate_list if isinstance(candidate_list, list) else [candidate_list]):
            j = extract_from_dict(item)
            if j: jobs.append(j)
    return jobs

def universal_export(company):
    """Parse all three tiers, deduplicate, export CSV."""
    print(f"\n[Export] Processing captured data for {company}...")
    all_jobs = {}

    def add_jobs(new_jobs, source):
        for j in new_jobs:
            jid = str(j.get("Job ID", "")).strip()
            if jid and jid not in all_jobs:
                all_jobs[jid] = j
                print(f"  [+] '{j['Job Title']}' (from {source})")

    # Tier 1: Network JSONs
    for f in glob.glob(os.path.join(NETWORK_DIR, f"net_{company}_*.json")):
        try:
            with open(f) as fh: content = json.load(fh)
            add_jobs(parse_json_response(content, content.get("url", "")), "T1-Network")
        except Exception as e:
            log_learning(company, f"Net parse fail: {f}", str(e))

    # Tier 2: DOM snapshots and Tier 3: Periodic snapshots
    for folder, label in [(DOM_DIR, "T2-DOM"), (SNAPSHOT_DIR, "T3-Snap")]:
        for f in glob.glob(os.path.join(folder, f"*_{company}_*.html")):
            try:
                with open(f, encoding="utf-8") as fh: html = fh.read()
                add_jobs(parse_google_html(html), f"{label}+Google")
                add_jobs(parse_json_ld(html), f"{label}+JSONLD")
            except Exception as e:
                log_learning(company, f"HTML parse fail: {f}", str(e))

    if all_jobs:
        out = os.path.join(BASE_DATA_DIR, f"{company}_manual_jobs.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Job Title","Job ID","Location","Description","Apply Link"])
            w.writeheader()
            w.writerows(all_jobs.values())
        print(f"[Export] ✅ Saved {len(all_jobs)} jobs → {out}")
    else:
        print(f"[Export] ⚠️  No jobs found in any tier for {company}")
    return all_jobs

# ── Main ──────────────────────────────────────────────────────────────────────
async def run(company):
    async with async_playwright() as p:
        print(f"[*] Universal Capture v3 — company={company}")
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR, headless=False,
            args=["--disable-blink-features=AutomationControlled"])
        page = await ctx.new_page()

        # Wire all three tiers
        page.on("response",
                lambda r: asyncio.ensure_future(handle_response(r, company)))
        page.on("framenavigated",
                lambda _: asyncio.ensure_future(handle_navigation(page, company)))

        print("\n[READY] Navigate to the career portal.")
        print("Commands: 'start' | 'stop' | 'quit'\n")

        snap_task = None

        while True:
            cmd = (await asyncio.get_event_loop().run_in_executor(
                None, input, "Command: ")).strip().lower()

            if cmd == "start":
                state["capturing"] = True
                snap_task = asyncio.ensure_future(periodic_snapshot_loop(page, company))
                print(">>> ✅ ALL THREE TIERS ACTIVE — click jobs now!")

            elif cmd == "stop":
                state["capturing"] = False
                if snap_task: snap_task.cancel()
                print(">>> ⏹  Capture stopped. Exporting...")
                break

            elif cmd == "quit":
                state["capturing"] = False
                if snap_task: snap_task.cancel()
                break

        universal_export(company)
        await ctx.close()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--company", required=True)
    args = p.parse_args()
    asyncio.run(run(args.company))

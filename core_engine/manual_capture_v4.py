"""
manual_capture_v4.py — Universal Passive Capture Engine with Discovery Loop
============================================================================
Four-Tier Architecture (100% Exhaustive):
  T1 - Network Layer     : All JSON/API/GraphQL responses (REST, XHR)
  T2 - DOM Layer         : Full page HTML on every navigation (SSR, MPA)
  T3 - Snapshot Layer    : Periodic body snapshots (SPA lazy-load, scroll)
  T4 - WebSocket Layer   : WS messages (streaming / real-time platforms)

Discovery Loop:
  1. Instruments everything on 'start'
  2. Analyzes the FIRST successful job capture to learn the site's pattern
  3. Gives the user EXACT instructions for repeating the pattern
  4. Counts captures in real-time and confirms each success
  5. [BETA] Automated mode: script replays the discovered pattern

Usage:
  python3 manual_capture_v4.py --company Google
  python3 manual_capture_v4.py --company Amazon --mode auto  [BETA]
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

# ── Config ────────────────────────────────────────────────────────────────────
USER_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", ".scraper_profile")
BASE_DATA_DIR = "/Users/satvikjain/Downloads/PM/data"
KB_FILE = "/Users/satvikjain/Downloads/PM/docs/Scraping_Career_Portals_Analysis.md"

RAW_NET  = os.path.join(BASE_DATA_DIR, "raw_network")
RAW_DOM  = os.path.join(BASE_DATA_DIR, "raw_dom")
RAW_SNAP = os.path.join(BASE_DATA_DIR, "raw_snapshots")
RAW_WS   = os.path.join(BASE_DATA_DIR, "raw_websocket")

for d in [RAW_NET, RAW_DOM, RAW_SNAP, RAW_WS]:
    os.makedirs(d, exist_ok=True)

# ── Shared State ──────────────────────────────────────────────────────────────
state = {
    "capturing":      False,
    "discovery_done": False,      # True after first successful job is learned
    "pattern":        None,       # Discovered pattern dict
    "capture_count":  0,          # Jobs captured so far
    "last_job_title": "",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S.%f")

def clean_html(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.replace('&nbsp;', ' ').replace('&amp;', '&').strip()

def log_learning(company, error, solution):
    entry = (f"\n### [{company}] Learning Case ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n"
             f"- **Error**: {error}\n- **Solution**: {solution}\n")
    try:
        with open(KB_FILE, "a") as f: f.write(entry)
    except: pass

def print_banner(msg, symbol="─"):
    line = symbol * 60
    print(f"\n{line}\n  {msg}\n{line}")

NOISE = [".js", ".css", ".png", ".jpg", ".svg", ".woff", ".ico",
         "google-analytics", "telemetry", "doubleclick", "gtm",
         "fonts.googleapis", "collect?v=", "favicon"]

# ── DISCOVERY ENGINE ──────────────────────────────────────────────────────────
def analyze_capture(captured_data: dict, tier: str, url: str) -> dict | None:
    """
    Given a captured blob, determine if it contains a real job.
    Returns a pattern dict if job found, else None.
    """
    # Try to extract a job title from the data
    def find_job_in_dict(d, depth=0):
        if depth > 5 or not isinstance(d, dict): return None
        title = d.get("name") or d.get("title") or d.get("job_title")
        job_id = d.get("id") or d.get("job_id") or d.get("displayJobId") or d.get("jobId")
        if title and job_id and any(kw in str(title).lower() for kw in 
                                    ["manager", "engineer", "analyst", "designer", "scientist", "developer"]):
            return {"title": str(title), "id": str(job_id), "tier": tier, "url_pattern": url}
        for v in d.values():
            if isinstance(v, dict):
                result = find_job_in_dict(v, depth+1)
                if result: return result
            elif isinstance(v, list):
                for item in v:
                    result = find_job_in_dict(item, depth+1) if isinstance(item, dict) else None
                    if result: return result
        return None

    if isinstance(captured_data, dict):
        return find_job_in_dict(captured_data)
    if isinstance(captured_data, list):
        for item in captured_data:
            result = find_job_in_dict(item) if isinstance(item, dict) else None
            if result: return result
    return None

def build_instructions(pattern: dict, company: str) -> str:
    """Generate exact user instructions based on the discovered pattern."""
    tier = pattern.get("tier", "T1")
    url  = pattern.get("url_pattern", "")

    if tier == "T1-Net":
        return (
            f"✅ PATTERN DISCOVERED ({company}) — API at:\n"
            f"   {url[:80]}\n\n"
            f"📋 INSTRUCTIONS:\n"
            f"   1. Go back to the job LISTING page.\n"
            f"   2. Click on each job CARD one-by-one to open the detail view.\n"
            f"   3. Wait ~2 seconds for each page to load fully.\n"
            f"   4. You do NOT need to scroll — just click & wait.\n"
            f"   5. When done with all jobs, type 'stop'.\n\n"
            f"   I will confirm each capture with '[✓ Captured]'"
        )
    elif tier in ("T2-Dom", "T3-Snap"):
        return (
            f"✅ PATTERN DISCOVERED ({company}) — SSR/HTML page:\n"
            f"   {url[:80]}\n\n"
            f"📋 INSTRUCTIONS:\n"
            f"   1. Go back to the job LISTING page.\n"
            f"   2. Click on each job CARD to open the detail page.\n"
            f"   3. Wait until the page fully loads (you can read the title).\n"
            f"   4. Press BACK, then open the next job.\n"
            f"   5. When done with all jobs, type 'stop'.\n\n"
            f"   I will confirm each DOM snapshot with '[✓ DOM Captured]'"
        )
    elif tier == "T4-WS":
        return (
            f"✅ PATTERN DISCOVERED ({company}) — WebSocket stream:\n"
            f"   {url[:80]}\n\n"
            f"📋 INSTRUCTIONS:\n"
            f"   1. Scroll through the job list — do NOT click cards.\n"
            f"   2. As you scroll, data streams in automatically.\n"
            f"   3. After each visible batch (~10 jobs), pause 2 seconds.\n"
            f"   4. Click 'Next Page' at the bottom if there is one.\n"
            f"   5. Type 'stop' when you've seen all jobs.\n\n"
            f"   I will confirm each WS batch with '[✓ WS Captured]'"
        )
    return (
        f"✅ PATTERN DISCOVERED ({company}) — combo mode.\n"
        f"📋 INSTRUCTIONS:\n"
        f"   1. Click each job card to open it.\n"
        f"   2. Wait 2 seconds on each detail page.\n"
        f"   3. Scroll to the bottom of each detail page.\n"
        f"   4. Type 'stop' when done.\n"
    )

# ── TIER 1: Network Layer ─────────────────────────────────────────────────────
async def handle_response(response, company):
    if not state["capturing"]: return
    url = response.url
    if any(p in url for p in NOISE): return
    try:
        ct = response.headers.get("content-type", "").lower()
        is_json = "json" in ct
        is_api  = any(k in url.lower() for k in
                      ["api/", "graphql", "v1/", "v2/", "/get", "results", "search", "jobs", "position", "detail"])
        if is_json or is_api:
            data = await response.json()
            path = os.path.join(RAW_NET, f"net_{company}_{ts()}.json")
            with open(path, "w") as f:
                json.dump({"url": url, "data": data}, f, indent=2)

            # Run discovery analysis
            job = analyze_capture(data, "T1-Net", url)
            if job and not state["discovery_done"]:
                state["discovery_done"] = True
                state["pattern"] = job
                state["capture_count"] += 1
                state["last_job_title"] = job["title"]
                print(f"\n  [✓ T1-Net] First job captured: '{job['title']}'")
                print(build_instructions(job, company))
            elif job:
                state["capture_count"] += 1
                state["last_job_title"] = job["title"]
                print(f"  [✓ Captured #{state['capture_count']}] '{job['title']}'")
    except: pass

# ── TIER 2: DOM Layer ─────────────────────────────────────────────────────────
async def handle_navigation(page, company):
    if not state["capturing"]: return
    try:
        await page.wait_for_load_state("networkidle", timeout=6000)
        html = await page.content()
        path = os.path.join(RAW_DOM, f"dom_{company}_{ts()}.html")
        with open(path, "w", encoding="utf-8") as f: f.write(html)

        # Check if page has a job — look for JSON-LD
        jobs_found = parse_json_ld(html)
        google_jobs = parse_google_af(html)
        all_found = jobs_found + google_jobs

        if all_found and not state["discovery_done"]:
            j = all_found[0]
            state["discovery_done"] = True
            state["pattern"] = {"title": j["Job Title"], "id": str(j["Job ID"]), "tier": "T2-Dom", "url_pattern": page.url}
            state["capture_count"] += 1
            state["last_job_title"] = j["Job Title"]
            print(f"\n  [✓ T2-DOM] First job captured: '{j['Job Title']}'")
            print(build_instructions(state["pattern"], company))
        elif all_found:
            state["capture_count"] += len(all_found)
            print(f"  [✓ DOM Captured #{state['capture_count']}] {len(all_found)} job(s) on page")
        else:
            print(f"  [T2-DOM] Page snapshot ({len(html)//1024}KB) — no jobs parsed yet")
    except Exception as e:
        pass

# ── TIER 3: Periodic Snapshot ─────────────────────────────────────────────────
async def periodic_snapshot_loop(page, company):
    last_hash = ""
    print("  [T3-Snap] Monitoring for content changes...")
    while state["capturing"]:
        try:
            html = await page.inner_html("body")
            h = hashlib.md5(html.encode()).hexdigest()
            if h != last_hash:
                path = os.path.join(RAW_SNAP, f"snap_{company}_{ts()}.html")
                with open(path, "w", encoding="utf-8") as f: f.write(html)
                last_hash = h
        except: pass
        await asyncio.sleep(2)

# ── TIER 4: WebSocket Layer ───────────────────────────────────────────────────
async def handle_websocket(ws, company):
    """Intercept all WebSocket messages for WS-based career portals."""
    async def on_message(msg):
        if not state["capturing"]: return
        try:
            data = json.loads(msg)
            path = os.path.join(RAW_WS, f"ws_{company}_{ts()}.json")
            with open(path, "w") as f:
                json.dump({"url": ws.url, "data": data}, f, indent=2)
            job = analyze_capture(data, "T4-WS", ws.url)
            if job and not state["discovery_done"]:
                state["discovery_done"] = True
                state["pattern"] = job
                state["capture_count"] += 1
                state["last_job_title"] = job["title"]
                print(f"\n  [✓ T4-WS] First job via WebSocket: '{job['title']}'")
                print(build_instructions(job, company))
            elif job:
                state["capture_count"] += 1
                print(f"  [✓ WS #{state['capture_count']}] '{job['title']}'")
        except: pass

    ws.on("framereceived", lambda payload: asyncio.ensure_future(on_message(payload.get("payload", ""))))

# ── PARSERS (all formats) ─────────────────────────────────────────────────────
def parse_google_af(html):
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
    jobs = []
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(m)
            items = (data.get('itemListElement', []) if data.get('@type') == 'ItemList'
                     else ([data] if data.get('@type') == 'JobPosting' else []))
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

def parse_network_json(content, url):
    jobs = []
    data = content.get("data", {})

    def from_dict(d):
        if not isinstance(d, dict): return None
        inner = d.get("data", d)
        if isinstance(inner, dict) and (inner.get("name") or inner.get("title")) and inner.get("id"):
            d = inner
        jid   = d.get("id") or d.get("displayJobId") or d.get("job_id") or d.get("jobId")
        title = d.get("name") or d.get("title") or d.get("job_title")
        if not (jid and title): return None
        jd   = d.get("jobDescription") or d.get("description") or d.get("basic_qualifications", "")
        locs = d.get("locations") or d.get("location")
        loc  = (locs[0] if isinstance(locs, list) and locs else locs) or ""
        link = (d.get("publicUrl") or d.get("positionUrl") or d.get("url")
                or d.get("url_next_step") or url)
        return {"Job Title": str(title), "Job ID": str(jid), "Location": str(loc),
                "Description": clean_html(jd), "Apply Link": link}

    j = from_dict(data if isinstance(data, dict) else content)
    if j: return [j]

    for key in ("jobs", "results", "items"):
        lst = (data.get(key) if isinstance(data, dict) else None) or (data if isinstance(data, list) else None)
        if lst:
            for item in (lst if isinstance(lst, list) else [lst]):
                r = from_dict(item)
                if r: jobs.append(r)
            if jobs: break
    return jobs

# ── UNIVERSAL EXPORT ─────────────────────────────────────────────────────────
def universal_export(company):
    print_banner(f"Exporting data for {company}...")
    all_jobs = {}

    def add(new_jobs, src):
        for j in new_jobs:
            jid = str(j.get("Job ID", "")).strip()
            if jid and jid not in all_jobs:
                all_jobs[jid] = j
                print(f"  [+] '{j['Job Title']}' ({src})")

    # T1 Network
    for f in glob.glob(os.path.join(RAW_NET, f"net_{company}_*.json")):
        try:
            c = json.load(open(f))
            add(parse_network_json(c, c.get("url", "")), "T1-Net")
        except Exception as e: log_learning(company, f"Net parse {f}", str(e))

    # T2 DOM + T3 Snapshots + T4 WS
    for folder, label in [(RAW_DOM,"T2-DOM"), (RAW_SNAP,"T3-Snap")]:
        for f in glob.glob(os.path.join(folder, f"*_{company}_*.html")):
            try:
                html = open(f, encoding="utf-8").read()
                add(parse_google_af(html), f"{label}+Google")
                add(parse_json_ld(html), f"{label}+JSONLD")
            except Exception as e: log_learning(company, f"HTML parse {f}", str(e))

    for f in glob.glob(os.path.join(RAW_WS, f"ws_{company}_*.json")):
        try:
            c = json.load(open(f))
            add(parse_network_json(c, c.get("url", "")), "T4-WS")
        except Exception as e: log_learning(company, f"WS parse {f}", str(e))

    if all_jobs:
        out = os.path.join(BASE_DATA_DIR, f"{company}_manual_jobs.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Job Title","Job ID","Location","Description","Apply Link"])
            w.writeheader(); w.writerows(all_jobs.values())
        print(f"\n[✅] Exported {len(all_jobs)} jobs → {out}")
    else:
        print("\n[⚠️]  No jobs found in any tier.")

    # Update KB
    pattern_txt = f"Pattern: {state['pattern']}" if state['pattern'] else "Pattern not discovered"
    log_learning(company, "Session complete", f"{state['capture_count']} captures. {pattern_txt}")
    return all_jobs

# ── MAIN ──────────────────────────────────────────────────────────────────────
BETA_WARNING = """
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  AUTOMATED MODE [BETA] — USE WITH CAUTION               ║
║  This mode is under active development and may be unstable.  ║
║  For production use, stick to manual mode (default).         ║
╚══════════════════════════════════════════════════════════════╝
"""

async def run_auto_mode(page, company):
    """[BETA] Automated mode — replays discovered pattern."""
    print(BETA_WARNING)
    await asyncio.sleep(2)
    if not state["pattern"]:
        print("[AUTO-BETA] No pattern discovered yet. Browse one job manually first.")
        return
    print(f"[AUTO-BETA] Repeating pattern for: {state['pattern']}")
    # Find all job card links on the current page and click each one
    try:
        links = await page.query_selector_all("a[href*='job'], a[href*='career'], a[href*='position']")
        print(f"[AUTO-BETA] Found {len(links)} potential job links on page")
        for i, link in enumerate(links[:10]):
            try:
                href = await link.get_attribute("href")
                if href:
                    print(f"  [AUTO-BETA] Navigating to job {i+1}: {href[:60]}...")
                    await page.goto(href if href.startswith("http") else f"https://{page.url.split('/')[2]}{href}")
                    await page.wait_for_load_state("networkidle", timeout=8000)
                    import random
                    await asyncio.sleep(random.uniform(2, 4))  # human-like delay
                    await page.go_back()
                    await page.wait_for_load_state("networkidle", timeout=5000)
            except Exception as e:
                print(f"  [AUTO-BETA] Error on job {i+1}: {e}")
    except Exception as e:
        print(f"[AUTO-BETA] Error: {e}")

async def run(company, mode="manual"):
    async with async_playwright() as p:
        print_banner(f"Universal Capture v4 | company={company} | mode={mode.upper()}")
        if mode == "auto":
            print(BETA_WARNING)

        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR, headless=False,
            args=["--disable-blink-features=AutomationControlled"])
        page = await ctx.new_page()

        # Wire all 4 tiers
        page.on("response",
                lambda r: asyncio.ensure_future(handle_response(r, company)))
        page.on("framenavigated",
                lambda _: asyncio.ensure_future(handle_navigation(page, company)))
        page.on("websocket",
                lambda ws: asyncio.ensure_future(handle_websocket(ws, company)))

        print("""
[HOW TO USE]
  1. The browser is open. Navigate to the career portal.
  2. Type 'start' — all 4 capture tiers will activate.
  3. Browse ONE job detail page. I'll learn the pattern and tell you EXACTLY what to do.
  4. Follow my instructions to capture remaining jobs.
  5. Type 'stop' when all jobs are captured.
  6. Type 'auto' to try automated capture [BETA — may be unstable].

Commands: start | stop | auto | quit | status
""")

        snap_task = None
        while True:
            cmd = (await asyncio.get_event_loop().run_in_executor(
                None, input, "Command: ")).strip().lower()

            if cmd == "start":
                state["capturing"] = True
                snap_task = asyncio.ensure_future(periodic_snapshot_loop(page, company))
                print_banner("ALL 4 TIERS ACTIVE — Browse one job now!", "═")
                print("  T1 ✅ Network (JSON/API/GraphQL)")
                print("  T2 ✅ DOM (full page HTML on navigation)")
                print("  T3 ✅ Snapshots (periodic — every 2s)")
                print("  T4 ✅ WebSockets (streaming data)")
                print("\n  → Click on a job detail page to begin discovery.")

            elif cmd == "stop":
                state["capturing"] = False
                if snap_task: snap_task.cancel()
                print(f"[Capture stopped] Total confirmed captures: {state['capture_count']}")
                break

            elif cmd == "auto":
                if mode != "auto":
                    print(BETA_WARNING)
                    confirm = (await asyncio.get_event_loop().run_in_executor(
                        None, input, "Type 'yes' to enable auto mode [BETA]: ")).strip().lower()
                    if confirm != "yes":
                        print("Auto mode cancelled.")
                        continue
                await run_auto_mode(page, company)

            elif cmd == "status":
                print(f"  Capturing: {state['capturing']}")
                print(f"  Discovery done: {state['discovery_done']}")
                print(f"  Pattern: {state['pattern']}")
                print(f"  Jobs captured: {state['capture_count']}")
                print(f"  Last job: {state['last_job_title']}")

            elif cmd == "quit":
                state["capturing"] = False
                if snap_task: snap_task.cancel()
                break

            else:
                print("  Commands: start | stop | auto | quit | status")

        universal_export(company)
        await ctx.close()

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Universal Passive Capture Engine v4")
    ap.add_argument("--company", required=True, help="Company name (e.g. Google, Amazon)")
    ap.add_argument("--mode", default="manual", choices=["manual", "auto"],
                    help="Capture mode: manual (default) or auto [BETA]")
    args = ap.parse_args()
    asyncio.run(run(args.company, args.mode))

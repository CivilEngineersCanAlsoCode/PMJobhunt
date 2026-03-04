# Sync — AI-Powered Resume Customization System

> **Self-serve, end-to-end resume customization for PM job applications.**
> One command sets up the entire pipeline: job data → signal extraction → tailored resume → GitHub Pages.

---

## What is Sync?

Sync is an AI-powered system that:

1. **Ingests** your career history (resume + notes) and target job descriptions
2. **Vectorizes** your career signals into a searchable knowledge base
3. **Customizes** a pixel-perfect HTML resume for each target role
4. **Hosts** all resumes on GitHub Pages with a master index

---

## Prerequisites

Install these before starting:

```bash
# Python 3.10+
python3 --version

# Playwright (for browser-based scrapers)
pip install playwright && playwright install chromium

# Beads CLI (task tracking)
pip install beads-cli

# Antigravity (AI orchestrator — the agent that runs this system)
# This system is designed to run inside Antigravity (Google DeepMind's agent IDE)
```

---

## Quick Start

### Option A — Automated (Recommended)

Run the activation workflow. Antigravity will guide you through every step interactively:

```
/activate-sync
```

This will:

1. Check your system dependencies
2. Ask for your Obsidian vault path (optional) and existing resume
3. Set up the Beads task graph
4. Walk you through getting job data
5. Run resume customization for each target role

---

### Option B — Manual Step-by-Step

#### Step 1: Get Job Data

You have 3 options. Pick whichever suits you:

**Option 1 — Manual CSV (simplest, no scraping)**

Copy and fill in the template:

```
data/manual_job_template.csv
```

Required columns: `Company`, `Job Title`, `Job ID`, `Location`, `Description`, `Apply Link`

Save your filled sheet as `data/final_job_batch.csv`.

**Option 2 — Universal Passive Capture (any career portal)**

Works for Amazon, Microsoft, Netflix — any portal with a JSON API:

```bash
python3 scripts/manual_capture_v4.py --company Amazon
```

1. A browser opens — navigate to the career portal
2. Type `start` in the terminal
3. Click into job detail pages — the script captures everything automatically
4. Type `stop` — data is exported as `data/Amazon_manual_jobs.csv`

> **How the discovery loop works:**
> After you open your first job, the script identifies the data pattern (REST API / SSR HTML / WebSocket) and prints **exact instructions** telling you whether to click cards, just scroll, or use the Next button.

**Option 3 — Google Careers Scraper (zero interaction)**

Google embeds jobs directly in page HTML — no browser needed:

```bash
python3 scripts/google_scraper.py
```

Outputs `data/Google_manual_jobs.csv` with all PM roles in India automatically.

#### Step 2: Build Final Job Batch

After gathering data for each company, consolidate into one CSV:

```bash
python3 scripts/build_final_batch.py
```

This picks the top 3 most relevant jobs per company and writes `data/final_job_batch.csv`.

Or just curate the 3 best roles from your CSVs manually and save as `data/final_job_batch.csv`.

#### Step 3: Provide Your Career Background

The system needs to understand you before it can customize your resume. You'll be asked for:

- **Existing resume**: any format (PDF, DOCX, HTML) — drop it in `Input/`
- **Career notes** (optional): Obsidian vault, notion export, or any `.md` files — also in `Input/`
- **Target brand color**: the hex color for each company (e.g., Google = `#4285F4`) — entered interactively

If you have no existing resume, Antigravity will interview you and build one from scratch.

#### Step 4: Run Resume Customization

```
/activate-sync
```

Antigravity reads your `final_job_batch.csv`, matches each role to your career signals, and outputs a tailored HTML resume in `output/` for each job.

---

## Data Privacy

All data stays **100% local**:

- No data is sent to external servers
- Scraped raw files are `.gitignore`d — they never leave your machine
- Only scripts, templates, and docs are in this repo

---

## File Structure

```
PM/
├── scripts/
│   ├── manual_capture_v4.py    ← Universal capture (any portal)
│   ├── google_scraper.py       ← Google Careers HTML parser
│   ├── microsoft_automation.py ← Microsoft Eightfold automation
│   ├── build_final_batch.py    ← Consolidate top jobs to CSV
│   └── discovery_engine.py     ← Pattern learning engine
│
├── data/
│   └── manual_job_template.csv ← Fill this manually if not scraping
│
├── Templates/
│   └── CV Format.html          ← Base resume template (DO NOT edit directly)
│
├── .agents/workflows/
│   ├── activate-sync.md        ← Main activation workflow
│   └── edit-template.md        ← Safe template editing workflow
│
├── research documents/
│   ├── resume_customization_plan.md     ← Full system spec
│   └── Scraping_Career_Portals_Analysis.md  ← Scraping knowledge base
│
└── AGENTS.md                   ← Agent configuration
```

---

## Scraper Reference

| Portal    | Method            | Script                                              | Notes                     |
| --------- | ----------------- | --------------------------------------------------- | ------------------------- |
| Google    | HTML parse        | `google_scraper.py`                                 | Zero interaction, instant |
| Amazon    | JSON API capture  | `manual_capture_v4.py`                              | Click each job card       |
| Microsoft | Headful browser   | `microsoft_automation.py` or `manual_capture_v4.py` | Automated or passive      |
| Any other | Universal capture | `manual_capture_v4.py`                              | Discovery loop guides you |

---

## Troubleshooting

**"No jobs found" from scraper**
→ Type `status` in the terminal during a capture session to see which tiers are active and what's been captured.

**Browser doesn't open**
→ Run `playwright install chromium` and try again.

**Resume not matching the JD well**
→ Add more career context to `Input/` — the more signals, the better the match.

**Template looks wrong**
→ Only edit the template via `/edit-template` (never directly) to preserve the base integrity.

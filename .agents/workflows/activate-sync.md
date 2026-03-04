---
description: Bootstrap and activate the Sync resume customization platform for a new user
---

# /activate-sync — Sync Platform Bootstrap Workflow

This workflow sets up the entire Sync platform from scratch for any new user and orients returning users to their current state.

## HOW TO USE

Type `/activate-sync` in any Antigravity session to trigger this workflow.

---

// turbo-all

## Step 1 — Verify bd Installation

Run `bd --version` to check if bd (Beads) is installed.
If the command is not found, run:

```bash
npm install -g @beads/cli
bd init
```

Then confirm with `bd --version`.

## Step 2 — Check Sync db Context

Run `bd context` to see if a Sync task graph already exists.

If the output shows open epics starting with `PM-SYNC-`, skip to **Step 10** (returning user flow).

If no context exists, this is a first-time setup. Proceed to Step 3.

## Step 3 — bd Task Graph Initialization

Run the following to create the full task structure. Execute sequentially:

```bash
cd /path/to/PM
bd create "Sync Platform: Career Signal Onboarding" -t epic -p 0
# Note the returned ID as EPIC_A

bd create "Run structured user interview (career history + metrics)" -t task -p 0
# Note as T01

bd create "Ingest all Resume Brain files into ChromaDB" -t task -p 0
# Note as T02

bd create "Create blank HTML resume template with placeholders" -t task -p 0
# Note as T03

bd create "Connect GitHub account and configure target repository" -t task -p 0
# Note as T04

bd create "Push blank template to GitHub and init Sync folder structure" -t task -p 0
# Note as T05

bd create "Sync Platform: JD Input and Data Acquisition" -t epic -p 0
# Note as EPIC_B

bd create "Step 4.0: Dynamic Career Portal Scraper (Optional)" -t task -p 0
# Note as T10 - Hybrid data collection mode

bd create "Read input CSV (Company, Website, JD)" -t task -p 0
# Note as T11

bd create "Parse JD into structured schema" -t task -p 0
# Note as T12

bd create "Query ChromaDB to retrieve top-k relevant signal entries" -t task -p 0
# Note as T13

bd create "Sync Platform: Resume Customization Engine" -t epic -p 0
# Note as EPIC_C

bd create "Phase 1: Intelligence Map (JD signal to experience)" -t task -p 0
bd create "Phase 2: Verification Interview (if gap exists)" -t task -p 0
bd create "Phase 3: Content Draft (XYZ bullets, 82-88 chars each)" -t task -p 0
bd create "Phase 4: Brand Research (company CSS color variables)" -t task -p 0
bd create "Phase 5: HTML Assembly (copy template, inject content)" -t task -p 0
bd create "Phase 6: Sub-Header Styling (pipe approach, black borders)" -t task -p 0
bd create "Phase 7: Date Column Validation (c5 ≥ 14.5%, no-wrap)" -t task -p 0
bd create "Phase 8: One-Line Bullet Validation (82-88 char count)" -t task -p 0
bd create "Phase 9: Compression Pass (exactly 1 page)" -t task -p 0
bd create "Phase 10: Match Score Calculation" -t task -p 0
bd create "Phase 11: GitHub Push (Sync/Company/Role/ folder)" -t task -p 0
bd create "Phase 12: Recruiter InMail + 300-char LinkedIn Invite" -t task -p 0

bd sync
```

Then wire all dependencies as described in `resume_customization_plan.md` Phase 0.2.

## Step 4 — Check ChromaDB Status

Run:

```bash
docker ps | grep chroma
```

**If ChromaDB container is NOT running**, start it with a **named volume** for persistent storage:

```bash
docker run -d --name chroma \
  -v /Users/satvikjain/Downloads/PM/chroma_data:/chroma/chroma \
  -p 8000:8000 \
  chromadb/chroma
```

> ⚠️ Uses a **local bind mount** (not Docker volume) so signals persist in `chroma_data/` inside the project folder across container restarts — no re-ingestion needed.
> If the container already exists (stopped): `docker start chroma`

**After ChromaDB is confirmed running**, perform a health check:

```python
import chromadb
client = chromadb.HttpClient(host="localhost", port=8000)
col = client.get_or_create_collection("career_signals")
count = col.count()
print(f"ChromaDB health: {count} career signals indexed.")
```

- If `count > 0` → signals are intact, proceed to Step 4b.
- If `count == 0` and `Resume Brain/chroma_backup_*.json` exists → auto re-ingest from backup:
  ```python
  import json, glob
  backup = sorted(glob.glob("Resume Brain/chroma_backup_*.json"))[-1]
  data = json.load(open(backup))
  col.add(documents=data["documents"], metadatas=data["metadatas"], ids=data["ids"])
  print(f"Re-ingested {len(data['ids'])} signals from backup.")
  ```
- If `count == 0` and no backup exists → trigger Step 6 (full ingestion).

**After every ingestion session (Step 6), export a JSON backup automatically:**

```python
backup_data = col.get(include=["documents", "metadatas"])
backup_data["ids"] = col.get()["ids"]
import json, datetime
fname = f"Resume Brain/chroma_backup_{datetime.date.today()}.json"
json.dump(backup_data, open(fname, "w"), indent=2)
print(f"Backup saved: {fname}")
```

If ChromaDB is running and healthy, proceed to Step 4b.

## Step 4b — Connect Obsidian Vault + Existing Resume ⭐ NEW

Ask the user:

**Obsidian Vault:**

> "Do you use Obsidian to journal your work or maintain a career/project log?
> If yes, paste the **absolute path** to your Obsidian vault folder."

- If path provided → scan for `.md` files in folders named `Resume Brain`, `Career`, `Projects`, `Work`, `Experience`
- List found files and confirm: "I found [N] files. I'll use these as your career signal source. Correct?"
- If no vault → flag and proceed to full user interview in Step 5.

**Existing Resume:**

> "Please paste the **absolute path** to your most recent resume (PDF or DOCX)."

- If provided → parse name, titles, all work experience (dates, roles, companies), education, skills
- Summarize: "I extracted [N] roles and [N] education entries. Does this look complete?"
- If no resume → flag and proceed to full user interview.

**Outcome Matrix:**
| Obsidian | Resume | Path |
|----------|--------|------|
| ✅ | ✅ | Pre-fill Step 1.1 profile → confirm with user (fast track) |
| ✅ | ❌ | Use vault, conduct partial interview for gaps |
| ❌ | ✅ | Parse resume, run structured interview for depth |
| ❌ | ❌ | Full empathetic Ultra Detail interview |

## Step 5 — User Onboarding Interview

Ask the user the structured interview questions in Phase 1.1 of `resume_customization_plan.md`.
Record the answers into `Resume Brain/interview_signal_YYYY-MM-DD.json`.

## Step 6 — Ingest Resume Brain into ChromaDB

For every `.md`, `.pdf`, `.txt` or `.json` file in the `Resume Brain/` folder:

- Parse content
- Chunk into 500-token segments
- Generate embeddings
- Store in ChromaDB collection `career_signals` with metadata fields: `source_file`, `company`, `role`

## Step 7 — Create Blank HTML Template

Copy `Templates/CV Format.html` to `Templates/Base_Template.html`.
Replace all content with placeholder HTML comments as defined in Phase 2.1 of `resume_customization_plan.md`.
Ensure the CSS guardrails are locked (`.c5 ≥ 14.5%`, `white-space: nowrap`, `--color-border: #000`).

## Step 8 — GitHub Setup

Ask the user:

1. "Please paste your GitHub Personal Access Token (needs `repo` scope)."
2. "Please paste the GitHub repository URL where your resumes will be stored."

Save these to `.env` (never commit this file).
Clone or connect to the repo, then create the `Sync/` folder scaffold.
Enable GitHub Pages from Settings → Pages → deploy from `main`.

## Step 9 — Ready State Confirmation (First Run Complete)

Print:

> "✅ Sync platform initialized successfully!
>
> - ChromaDB: [X] career signals indexed
> - GitHub Pages: Live at https://[username].github.io/[repo]/
> - Next step: Add your job batch to `Input/job_batch.csv`
>   Format: Company, Website, Role, JD
>   Then type `/activate-sync` again to start customizations."

Run `bd sync && git push` to save state.

---

## Step 10 — Returning User Flow

If `bd context` shows existing Sync epics, run:

```bash
bd ready --json
bd context
```

Display:

> "Welcome back to Sync. Your current context:
> Active Epic: [EPIC_NAME]
> Next unblocked task: [TASK_ID] — [TASK_NAME]
> Ready to continue? (yes/no)"

If user says yes, claim the task (`bd update <id> -s in_progress`) and execute it according to the corresponding Phase in `resume_customization_plan.md`.

---

## Step 11 — Start Customization Batch Loop

If `Input/job_batch.csv` exists and has unprocessed rows, begin the loop:

For each CSV row:

1. Data Acquisition (Step 4.0) → Choose Manual CSV or Dynamic Scrape
2. Parse JD → Phase 4.2 (PM-SYNC-12)
3. Query ChromaDB → Phase 4.3 (PM-SYNC-13)
4. Run Phases 5.1 through 5.12 sequentially with atomic bd task tracking
5. Push to GitHub and generate recruiter artifacts
6. Prompt user for next application or exit

---

_Reference: full process details are in `/Users/satvikjain/Downloads/PM/resume_customization_plan.md`_

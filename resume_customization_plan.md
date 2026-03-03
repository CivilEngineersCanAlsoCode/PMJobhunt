# SYNC — Resume Customization Master Plan

> **Version:** 3.0 (Scalable Platform Design)
> **Output Format:** HTML + CSS (GitHub Pages hosted)
> **Trigger:** `/activate-sync` workflow command
> **Orchestrator:** Antigravity (Claude Code CLI)

---

## SYSTEM OVERVIEW

Sync is an AI-powered, signal engineering resume customization system. It:

1. Captures and vectorizes user career signals into ChromaDB
2. Parses any target Job Description into a structured schema
3. Semantically retrieves the most relevant experience snippets per JD
4. Constructs a pixel-perfect, one-page, brand-colored HTML/CSS resume
5. Hosts it on GitHub Pages under a structured folder hierarchy
6. Tracks the application with a match score and application details file

The system is **self-serve** — a new user with zero context triggers `/activate-sync` and the workflow guides them through every stage, including onboarding, GitHub setup, ChromaDB ingestion, and the first batch of resume customizations.

---

## PHASE 0: `/activate-sync` — Platform Bootstrap Workflow

**File:** `.agents/workflows/activate-sync.md`
**Trigger:** User types `/activate-sync` in any new Antigravity session

### Step 0.1 — Dependency Check & System Health

- Check if `bd` CLI is installed (`bd --version`). If not, install it and run `bd init`.
- Check for existing `bd` context using `bd context`. If empty, initialize the Sync epic structure.
- Check if ChromaDB Docker container is running (`docker ps | grep chroma`). If not present, flag for user with instructions to `docker run` it (ChromaDB is self-hosted; cannot auto-start without approval).
- Check if `.agents/workflows/activate-sync.md` exists. If it does, skip bootstrap and jump to Step 0.3.

### Step 0.2 — bd Task Graph Initialization (First Run Only)

Create the following `bd` epics and tasks in one command sequence and link dependencies:

```
EPIC: PM-SYNC-00   "Sync Platform: Career Signal Onboarding"
  TASK: PM-SYNC-01   "Run structured user interview (career history + metrics)"
  TASK: PM-SYNC-02   "Ingest all Resume Brain files into ChromaDB"
  TASK: PM-SYNC-03   "Create blank HTML resume template with placeholders"
  TASK: PM-SYNC-04   "Connect GitHub account and configure target repository"
  TASK: PM-SYNC-05   "Push blank template to GitHub → init Sync/ folder structure"

EPIC: PM-SYNC-10   "Sync Platform: JD Input + Batch Loop Setup"
  TASK: PM-SYNC-11   "Read input CSV (Company, Website, JD)"
  TASK: PM-SYNC-12   "Parse JD → structured schema (keywords, skills, metrics expected)"
  TASK: PM-SYNC-13   "Query ChromaDB → retrieve top-k most relevant signal entries"

EPIC: PM-SYNC-20   "Sync Platform: Resume Customization Engine (Per Application)"
  TASK: PM-SYNC-21   "Phase 1: Intelligence Map (JD ↔ Experience signals)"
  TASK: PM-SYNC-22   "Phase 2: Verification Interview (if gap exists)"
  TASK: PM-SYNC-23   "Phase 3: Content Draft (XYZ bullets, 82-88 chars each)"
  TASK: PM-SYNC-24   "Phase 4: Brand Research (Colors CSS variables)"
  TASK: PM-SYNC-25   "Phase 5: HTML Assembly (copy template, inject content)"
  TASK: PM-SYNC-26   "Phase 6: Sub-Header Styling (pipe approach, border = #000)"
  TASK: PM-SYNC-27   "Phase 7: Date Column Validation (c5 ≥ 14.5%, nowrap)"
  TASK: PM-SYNC-28   "Phase 8: One-Line Bullet Validation (no wrapping, char count)"
  TASK: PM-SYNC-29   "Phase 9: Compression Pass (ensure 1 page exactly)"
  TASK: PM-SYNC-30   "Phase 10: Match Score Calculation"
  TASK: PM-SYNC-31   "Phase 11: GitHub Push (Sync/<Company>/<Role>/ folder)"
  TASK: PM-SYNC-32   "Phase 12: Generate Recruiter InMail + 300-char Invite"

EPIC: PM-SYNC-40   "Sync Platform: Presentation (Why Me Slides)"
  TASK: PM-SYNC-41   "Create frontend Claude skills slide deck (Why Me)"

Dependencies:
  PM-SYNC-02 → PM-SYNC-01 (Interview must happen before ingestion)
  PM-SYNC-03 → PM-SYNC-02 (Template created after signals ingested)
  PM-SYNC-05 → PM-SYNC-04 (Repo push needs GitHub connected)
  PM-SYNC-11 → PM-SYNC-05 (Batch loop starts after setup complete)
  PM-SYNC-12 → PM-SYNC-11 (JD parsing after CSV input)
  PM-SYNC-13 → PM-SYNC-12 (Retrieval after JD parsed)
  PM-SYNC-21 → PM-SYNC-13 (Customization after signals retrieved)
  PM-SYNC-22 → PM-SYNC-21 (Interview if gaps found in intellignce map)
  PM-SYNC-23 → PM-SYNC-22 (Draft after verification)
  PM-SYNC-24 → PM-SYNC-21 (Brand research runs parallel to interview)
  PM-SYNC-25 → PM-SYNC-23, PM-SYNC-24 (Assembly needs draft + brand)
  PM-SYNC-26 → PM-SYNC-25 (Styling after assembly)
  PM-SYNC-27 → PM-SYNC-26 (Date validation after layout set)
  PM-SYNC-28 → PM-SYNC-27 (Bullet check after date check)
  PM-SYNC-29 → PM-SYNC-28 (Compression after all bullets pass)
  PM-SYNC-30 → PM-SYNC-29 (Score after resume is finalized)
  PM-SYNC-31 → PM-SYNC-30 (Push after score done)
  PM-SYNC-32 → PM-SYNC-31 (Recruiter messages after push)
```

### Step 0.3 — Context Recovery (Subsequent Sessions)

- Run `bd ready --json` to see the next unblocked task.
- Run `bd context` to display the current active branch and active epic.
- Announce the current state and prompt: "Welcome back to Sync. Your next task is [PM-SYNC-XX]. Want to continue?"

---

## PHASE 1: USER ONBOARDING (Career Signal Capture)

### Step 1.1 — Structured User Interview (PM-SYNC-01)

Conduct a guided Q&A to extract structured career signals. Questions are organized by category:

**Career Identity:**

- Full name, current title, years of full PM experience, current/target CTC
- Target role type (FAANG PM, SaaS PM, Consulting PM)

**For EACH Work Experience (most recent first):**

- Company name, official title, duration
- What did you own? (product area + user base size)
- What was your biggest measurable impact? (quantify with %)
- What technology/AI/ML did you work with?
- What was the hardest stakeholder challenge?
- Any awards, LORs, promotions?

**Competitive Exam & Academic Records:**

- Scores, ranks, institution names, years

**Projects & Side Work:**

- Name, role, outcome (GitHub links, demos if any)

All answers stored in structured JSON format: `Resume Brain/interview_signal_YYYY-MM-DD.json`

### Step 1.2 — Resume Brain Ingestion into ChromaDB (PM-SYNC-02)

For every file inside `Resume Brain/`:

1. Parse and chunk the text content (500-token chunks with 50-token overlap)
2. Generate embeddings via the active embedding model
3. Store in ChromaDB collection `career_signals` with metadata:
   - `source_file`, `company`, `role`, `year`, `impact_type`
4. Confirm storage with a count check

> **Note:** ChromaDB requires Docker to be running. If Docker is not active, this step will pause and display: _"ChromaDB requires Docker. Please run: `docker start chroma`. Then type `/activate-sync` again."_

---

## PHASE 2: BASE TEMPLATE SETUP

### Step 2.1 — Create Blank HTML Template with Placeholders (PM-SYNC-03)

Copy `Templates/CV Format.html` into `Templates/Base_Template.html`.

Replace all content sections with clearly annotated placeholder text:

```html
<!-- HEADER -->
<span class="name">{{FULL_NAME}}</span>
<span class="meta">| {{GENDER}} | {{AGE}}</span>

<!-- TAGBAR: 4 most relevant signal phrases for this company -->
<div class="t">{{TAGBAR_1: e.g. "IIT Delhi Alumnus"}}</div>
...

<!-- Professional Summary: 3 lines, justified, 82-88 chars per line -->
<td class="dsc">
  {{PROFESSIONAL_SUMMARY_LINE_1}} ...

  <!-- Experience Row: Each role gets one .sub row + labeled .dsc rows -->
</td>

<td class="tl">{{COMPANY_NAME}}</td>
<td>{{ROLE_TITLE}}</td>
<td>{{ROLE_TAGS: 3 signal phrases | piped}}</td>
<td>{{DATE_START}} – {{DATE_END}}</td>
```

#### Key CSS Rules (always preserved in template):

```css
/* Grid: c5 must remain ≥ 14.5% to prevent date clipping */
colgroup .c0 {
  width: 3.9%;
}
.c1 {
  width: 12%;
}
.c2 {
  width: 29.5%;
}
.c3 {
  width: 11.9%;
}
.c4 {
  width: 28.2%;
}
.c5 {
  width: 14.5%;
}

/* Date cells: never wrap */
.sub td:last-child {
  white-space: nowrap;
}
.yr {
  white-space: nowrap;
}

/* Sub-header: company row — PIPE approach, no heavy background */
.sub {
  background: #f8f8f8;
  color: #111;
  border-bottom: 1.5px solid #000;
}
.sub td {
  font-weight: 600;
  text-align: left;
}

/* Borders: all table borders pitch black */
--color-border: #000000;

/* Typography: retain Sans-Serif, scale to 9pt */
body {
  font-family: "Segoe UI", Calibri, Arial, sans-serif;
  font-size: 9pt;
  line-height: 1.4;
}

/* Bullet density targeting */
.dsc {
  font-size: 8.5pt;
  line-height: 1.35;
}
.dsc ul {
  padding-left: 14px;
}
.dsc li {
  margin-bottom: 1px;
}

/* Micro-stretch utilities for final ~1-3mm gap adjustment */
.stretch-1 {
  letter-spacing: 0.15px;
  word-spacing: 1px;
}
.stretch-2 {
  letter-spacing: 0.3px;
  word-spacing: 2px;
}

/* Spacer between jobs (visual breathing room) */
.spacer td {
  height: 6px;
  border: none !important;
}
```

---

## PHASE 3: GITHUB SETUP (PM-SYNC-04, PM-SYNC-05)

### Step 3.1 — Connect GitHub

Ask user:

1. "Paste your GitHub Personal Access Token (with `repo` scope)."
2. "Paste the full URL of the GitHub repository where resumes will be stored."

Store these in a local `.env` file (never committed to git).

### Step 3.2 — Initialize Sync Folder Structure

After cloning or connecting to the repo, create:

```
Sync/
  README.md           ← Platform overview + how to read match scores
  <Company_Name>/
    <Role_Name>/
      resume.html     ← Branded, hosted resume
      application_details.md ← JD, key requirements, match score, GitHub Pages link
```

Push the empty scaffolding with an initial commit: `"chore: init Sync folder structure"`.

Enable GitHub Pages from the root of the repository (Settings → Pages → Deploy from branch `main`).

---

## PHASE 4: JD INPUT LOOP

### Step 4.1 — Input CSV Format (PM-SYNC-11)

The user provides a file at `Input/job_batch.csv`:

```csv
Company,Website,Role,JD
Google,https://google.com,PM - Search,"Full JD text here..."
Amazon,https://amazon.com,Senior PM - Alexa,"Full JD text here..."
```

One resume customization cycle will run **per row**, sequentially.

### Step 4.2 — JD Parsing (PM-SYNC-12)

For each row, parse the JD into a structured schema:

```json
{
  "company": "Google",
  "role": "PM - Search",
  "required_skills": ["AI/ML", "Search Ranking", "Data-Driven"],
  "required_metrics": ["DAU", "Latency", "Engagement"],
  "seniority_signals": ["cross-functional", "ambiguous environments"],
  "keyword_cluster": ["Agentic", "LLM", "Retrieval systems"]
}
```

### Step 4.3 — ChromaDB Retrieval (PM-SYNC-13)

Query ChromaDB collection `career_signals` with the combined JD embedding to retrieve the top-8 most semantically relevant signal entries. These become the "evidence pool" for content drafting.

---

## PHASE 5: RESUME CUSTOMIZATION ENGINE (Per Application)

> Every sub-task below corresponds to an atomic `bd` task. Each must be completed and verified before the next begins.

### Phase 5.1 — Intelligence Map (PM-SYNC-21)

Create `Sync/<Company>/<Role>/intelligence_map.md`:

- Map each JD required skill → to a matching experience snippet from the signal pool
- Identify any critical gaps (skills required but not in evidence pool)
- Define 4 Tagbar signal phrases for this company
- Define the "Top-Third Marketing Pitch" (who Satvik is for _this_ company)

### Phase 5.2 — Verification Interview (PM-SYNC-22)

If any gap exists from the Intelligence Map:

- Prompt the user with targeted questions (e.g., "You need 'Search API experience' for this role. Tell me one time you worked with APIs or search infrastructure?")
- Store answers in ChromaDB for future use
- Gate: Only proceed to Phase 5.3 after user confirms or skips all gap questions

### Phase 5.3 — Content Draft (PM-SYNC-23)

Draft the full resume content in `Sync/<Company>/<Role>/content_draft.md`:

**Rules (NON-NEGOTIABLE):**

| Rule                | Standard                                                             |
| ------------------- | -------------------------------------------------------------------- |
| Bullet format       | Google XYZ: "Accomplished [X] as measured by [Y] by doing [Z]"       |
| Character count     | 82–88 characters per bullet (including spaces, for 9pt @ A4 width)   |
| Line count          | Exactly 1 line per bullet — ZERO wrapping allowed                    |
| Bold keywords       | Every bullet: 2-4 bold terms                                         |
| Metric density      | Every bullet: at least 1 number/%                                    |
| Fabrication rule    | NEVER invent metrics — only use verified numbers from signal pool    |
| Trailing adjustment | Max 10 `&nbsp;` to close minor (<3mm) gap. For major gaps, rephrase. |

For each role's sub-sections, draft enough bullets to fill exactly the available vertical space (no overflow, no bottom whitespace).

### Phase 5.4 — Brand Research (PM-SYNC-24)

Search the web for `<company> official brand colors hex codes`. Store in CSS variables:

```css
--color-primary: #HEX; /* Primary brand color → section headers */
--color-secondary: #HEX; /* Secondary color → tagbar background */
--color-accent: #HEX; /* CTA / link color */
```

### Phase 5.5 — HTML Assembly (PM-SYNC-25)

1. Copy `Templates/Base_Template.html` → `Sync/<Company>/<Role>/resume.html`
2. Inject all content from `content_draft.md` into the HTML placeholders
3. Apply brand color CSS variables at the top of the `<style>` block
4. Apply the Sub-Header pipe approach: each `.sub` row contains `Company | Role | Tag1 | Tag2 | Tag3 | Date`

### Phase 5.6 — Sub-Header Visual Overhaul (PM-SYNC-26)

Replace heavy `.sub td` dark backgrounds with:

```css
.sub {
  background: #f5f5f5;
  color: #111111;
  border-top: 2px solid #000;
  border-bottom: 1px solid #000;
}
.sub td {
  font-weight: 700;
  padding: 3px 5px;
}
```

Company name gets left-aligned. Role gets center alignment. Date gets right alignment with `white-space: nowrap`.

### Phase 5.7 — Date Column Validation (PM-SYNC-27)

Automated check:

- Assert `colgroup .c5 { width: 14.5% }` is present in the CSS
- Assert `.yr` and `.sub td:last-child` both have `white-space: nowrap`
- Visually confirm no date string exceeds 20 chars (format: `MMM'YY – MMM'YY` or `MM/YYYY – Present`)
- **Hard Stop:** If dates are clipping in browser preview, increase `.c5` to `16%` and reduce `.c2` and `.c4` by `0.75%` each.

### Phase 5.8 — Bullet Line Validation (PM-SYNC-28)

For each `<li>` element, verify:

1. Character count is between 82 and 92 (count using a script: `grep -o '.' | wc -c`)
2. No `<br>` tags exist inside any `<li>`
3. No line visually wraps when rendered in Chrome at 100% zoom on A4 size
4. Apply `class="stretch-1"` to bullets in the 75-81 char range
5. Rephrase (add 3-6 words of genuine context) any bullet under 75 chars
6. Trim (remove lowest-value words) any bullet over 92 chars

### Phase 5.9 — Compression Pass — 1 Page Check (PM-SYNC-29)

Render the HTML. Check if the content fits inside exactly 297mm vertical height.

- If overflowing: reduce `.spacer td { height }` from 6px → 4px, reduce `.dsc` line-height from 1.35 → 1.28
- If underflowing: increase spacer heights, or increase font-size by 0.5pt steps
- Repeat until content touches the bottom footer with zero white space

### Phase 5.10 — Match Score Calculation (PM-SYNC-30)

Score the resume against the JD schema:

- +10 pts for each JD-required keyword present in the resume
- +5 pts for each matching metric type (e.g., JD mentions "TRT", resume mentions "TRT")
- +5 pts if all 4 tagbar slots map to JD signals
- -10 pts for each JD-required skill with zero coverage
- Cap at 100. Initial score often 55–70%. Target: ≥90%.

### Phase 5.11 — GitHub Push (PM-SYNC-31)

```bash
git add Sync/<Company>/<Role>/
git commit -m "feat: add resume for <Company> - <Role>"
git push
```

Create `Sync/<Company>/<Role>/application_details.md`:

```markdown
# Application: <Company> — <Role>

## Match Score: XX/100

**Target: ≥90/100**

## GitHub Pages Link

https://<username>.github.io/<repo>/Sync/<Company>/<Role>/resume.html

## Key JD Requirements

1. ...
2. ...

## Full Job Description

<paste JD here>
```

### Phase 5.12 — Recruiter Artifacts (PM-SYNC-32)

**Recruiter InMail (≤300 words):**

```
Hi [Recruiter Name],

I came across the [Role] opening at [Company] and I'm genuinely excited about the alignment.

I've spent [X] years at [companies like Amex/Sprinklr], where I [1 SHARP credential].

For [Company], specifically, I believe I can [direct alignment to Company's JD signal].

I've attached my tailored resume: [GitHub Pages Link]

Would love to connect for a quick 15-minute call.

[Name]
```

**LinkedIn Connect Message (≤300 characters):**

```
Hi [Name], I'm applying to [Role] at [Company]. My work on [1 crisp signal from JD] aligns directly. Would love to connect and learn more about the team. [Link]
```

---

## PHASE 6: LOOP CONTROL

After completing Phases 5.1–5.12 for one row:

- Mark `PM-SYNC-20` subtasks closed in bd
- Prompt: "✅ [Company] - [Role] complete. Match Score: XX/100. Ready for next application? (yes/no)"
- If yes: move to next CSV row, re-start Phase 4.2 with fresh JD
- If no: save state, run `bd sync`, `git push`, and exit

---

## PHASE 7: FUTURE ARTIFACTS (Later Phases)

These are queued for development after Phase 1 MVP is stable:

| Artifact                                    | Status                |
| ------------------------------------------- | --------------------- |
| "Why Me" Slide Deck (frontend Claude skill) | PM-SYNC-41 — Queued   |
| LinkedIn narrative update                   | Roadmap (3-6 months)  |
| Interview simulation engine                 | Roadmap (6-12 months) |
| SaaS hosted version                         | Roadmap (12+ months)  |

---

## CONSTRAINTS & GUARDRAILS (Always Active)

1. **Never fabricate metrics** — only use verified numbers from signal pool or user interview
2. **`Base_Template.html` is immutable** — only editable via `/edit-template` workflow (requires explicit user confirmation + versioned backup)
3. **Max 10 `&nbsp;`** for micro text gap adjustment — rephrase for major gaps
4. **Date column `.c5` ≥ 14.5% always** — never reduce below this
5. **`white-space: nowrap` on all date cells** — absolute rule
6. **82-92 char target per bullet** — validate with char count script
7. **1 page only** — hard stop, no exceptions
8. **XYZ formula for every bullet** — Accomplished X measured by Y by doing Z
9. **Border color: `#000000` only** — no gray borders
10. **Sub-header: pipe approach** — no heavy dark backgrounds

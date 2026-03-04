# SYNC — Resume Customization Master Plan

> **Version:** 4.0 (Obsidian Vault + Gap Confidence Gate + Epic Renumbering)
> **Output Format:** HTML + CSS (GitHub Pages hosted)
> **Trigger:** `/activate-sync` workflow command
> **Orchestrator:** Antigravity (Claude Code CLI)

---

## SYSTEM OVERVIEW

Sync is an AI-powered, signal engineering resume customization system. It:

1. Connects to user's Obsidian vault + existing resume to extract career signals
2. Captures and vectorizes career signals into ChromaDB (Q&A chunked format)
3. Parses each target JD and confirms ≥90% confidence before customizing
4. Constructs a pixel-perfect, one-page, brand-colored HTML/CSS resume
5. Hosts all resumes on GitHub Pages with a master README.md index
6. Tracks each application with a match score + recruiter artifacts
7. **Automates the entire lifecycle via GitHub Actions (CI/CD)**

> 🔒 **BASE TEMPLATE IS IMMUTABLE:** `Templates/Base_Template.html` is locked after initial creation.
> It may **only** be modified via the `/edit-template` command.
> The customization engine always **copies** the template — never edits it in place.

---

## EPIC 0: Platform Bootstrap (`/activate-sync`)

**File:** `.agents/workflows/activate-sync.md`

### Step 0.1 — Dependency Check & System Health

- Check if `bd` CLI is installed. If not, install and `bd init`.
- Run `bd context` — if Sync epics exist, skip to Step 0.5 (returning user).
- Check for ChromaDB Docker container (`docker ps | grep chroma`). If absent, pause and instruct user.

### Step 0.2 — bd Task Graph Initialization (First Run Only)

Create all epics, tasks, and dependencies as listed below in the bd dependency graph section.

### Step 0.3 — Context Recovery (Returning Users)

- Run `bd ready --json` + `bd context`
- Print: "Welcome back to Sync. Your next unblocked task is [PM-SYNC-XX]. Continue?"

### Step 0.4 — Obsidian Vault + Existing Resume Connection ⭐ NEW

Ask the user two things:

**A) Obsidian Vault:**

> "Do you use Obsidian for note-taking or maintaining a career/project journal?
> If yes, please paste the **absolute path** to your Obsidian vault folder."

- If path provided → scan for any `.md` files inside folders named `Resume Brain`, `Career`, `Projects`, `Work`, `Experience`, or at the vault root.
- List all found files to user and confirm: "I found [N] files in your vault. I'll use these as your career signal source. Does this look right?"
- If no vault → flag and proceed to Epic 1 structured interview.

**B) Existing Resume:**

> "Please paste the **absolute path** to your most recent resume (PDF or DOCX)."

- If file provided → parse it to extract: name, current title, all work experiences with dates and roles, academic records, skills/tools listed.
- Summarize extraction: "I extracted [N] work experiences, [N] education entries, and the following skills: [...]. Does this look complete?"
- If no resume → flag and proceed to structured interview.

**Outcome Paths:**
| Obsidian | Resume | Action |
|----------|--------|--------|
| ✅ | ✅ | Pre-fill Step 1.1 and confirm with user (fast track) |
| ✅ | ❌ | Use vault as signal source, conduct partial interview for resume details |
| ❌ | ✅ | Parse resume, conduct vault-equivalent structured interview |
| ❌ | ❌ | Conduct full empathetic multi-step interview (Ultra Detail mode) |

---

## EPIC 1: User Onboarding + Career Signal Capture

### Step 1.1 — User Profiling & Assumption Confirmation ⭐ UPDATED

**If Obsidian + Resume were both provided:**
Pre-fill a structured profile from the extracted data and present it to the user:

```
Here is what I know about you so far. Please confirm or correct:

👤 IDENTITY
Name: Satvik Jain | Age: 27 | Gender: Male
Current Title: Senior Associate Product Manager
Current Company: American Express
Current CTC: [?] | Target CTC: [?]
Target Roles: PM at FAANG / Global SaaS

💼 EXPERIENCE (most recent first)
1. Amex (Jul 2024 – Present): AML scoring, AI/ML, 30M+ daily txns
   → Assumed impact: Increased throughput / Reduced risk exposure [Confirm %?]
2. Sprinklr (Apr 2022 – Jul 2024): LLM support tooling, Walmart project
   → Assumed metric: 85% time-to-insight reduction [Confirm?]
3. Sukha Education (Jan 2025 – Present, Voluntary): NGO digital transformation
   → Assumed: Cost savings ₹60K, 50+ volunteers [Confirm?]

🎓 EDUCATION
IIT Delhi (B.Tech) | CGPA: [?] | Year: [?]

🛠 SKILLS
AI/ML, LLM Products, Agentic Frameworks, SaaS, Cross-functional leadership

❓ GAPS I NEED YOU TO FILL
- What is your current and target CTC?
- What was your exact CGPA / scores?
- Any CAT/GMAT/other competitive exam results?
- Any awards, promotions, or LORs received?
```

User can confirm, correct, or add to each section. All corrections are immediately stored.

**If partial or no data was provided:**
Run the full empathetic multi-step interview below.

---

### 🗣️ Full User Interview — Ultra Detail Mode (When Data is Missing)

> ℹ️ **Tone:** Behave like a college senior helping a friend build their first strong resume. Be warm, practical, and encouraging. Acknowledge uncertainty. Suggest reasonable assumptions when exact data isn't available.

> 📊 **Progress:** Print a progress indicator before every question: `[Session A of 5 | Question 1 of 6 | ~30 min total remaining]`
> 💾 **Auto-save:** After each session completes, save answers to `Resume Brain/interview_progress.json`. If `/activate-sync` is re-run, detect this file and skip completed sessions automatically.
> 🔘 **Optional Sessions:** Sessions C, D, E are marked OPTIONAL after A+B complete. User can proceed with partial profile and return later.

The interview is broken into 5 sequential sessions. Each session can be paused and resumed.

**Session A: Who Are You?**

```
Let's start with the basics! This helps me understand where you are and where you want to go.

1. What's your full name?
2. What's your current job title? (Don't worry if it doesn't say "PM" — tell me what you actually do)
3. Which company are you currently at, and for how long?
4. What's your current salary range? (Rough range is fine, this helps me gauge seniority signals)
5. What kind of roles are you targeting? (e.g., FAANG PM, B2B SaaS PM, Fintech PM)
6. Is there a specific company or type of company you're most excited about?
```

**Session B: Your Work (One Role at a Time)**
For each role (most recent first), ask:

```
Let's talk about your time at [Company]. This is where your strongest stories live!

1. What was your official title vs what you actually did day-to-day?
2. What product or feature were you most responsible for?
   (If you're not sure how to describe it, just tell me what problem it solved for users)
3. How many people used your product? (rough estimate is totally fine — even "tens of thousands")
4. What's the one thing you're most proud of building or delivering there?
5. Do you remember any numbers? (e.g., % faster, % more revenue, cost saved, users grown)
   → If not: "Think of it this way — before you made the change, what happened? After, what changed?"
   → Suggest: "Was it like a 20-30% improvement? Or more like 2x? Even a rough estimate helps."
6. Did you lead anyone? Team size? Cross-functional teams?
7. Did you work with engineers? Data scientists? Did you write PRDs or run sprints?
8. Any awards, LinkedIn shoutouts, performance ratings, LORs from this role?
```

**Session C: Academic & Exam Records**

```
Quick one — your academic background matters more than you think for FAANG applications!

1. Where did you do your undergrad? What stream? What year did you graduate?
2. What was your CGPA or percentage? (Even approximate is fine)
3. Did you appear for CAT, GMAT, GRE, JEE, or any other competitive exam?
   - If yes: Which ones, what year, and what was your score/percentile/rank?
4. Any academic projects or thesis work that involved analytics, tech, or business?
```

**Session D: Projects, Side Work & Extras**

```
Beyond your main job, what else have you built or contributed to?

1. Any personal projects, freelance work, or volunteer roles?
2. Any GitHub repos, live products, or portfolio links?
3. Any courses, certifications, or workshops relevant to PM/AI/ML?
4. Any community involvement — hackathons, conferences, writing, teaching?
```

**Session E: Aspirations & Gap Awareness**

```
Last one — and this one is really important for matching you to the right roles.

1. What excites you most about the roles you're applying for?
2. Is there anything in the JDs you're seeing that you feel you lack?
   (Be honest — knowing the gaps helps me help YOU prepare for them)
3. Are you open to roles that are slightly different from your exact experience?
   (e.g., adjacent industries, slightly different user segments)
4. Any specific companies you'd love to work at, and why?
```

---

### Step 1.2 — ChromaDB Ingestion (Q&A Chunked Format)

After the profile is confirmed, ingest all career signals into ChromaDB.

**Step 1.2a — Obsidian Vault Relevance Filter (Pre-Ingestion Gate)**

Before any Obsidian `.md` file is chunked, run a relevance check:

```
Prompt: "Does this note contain career-relevant information about work experience,
projects, achievements, skills, or academic background? Answer: Yes or No only."
```

- **Yes** → proceed to chunking for this file
- **No** → skip this file, log filename to `Resume Brain/vault_skipped_files.log`

Print summary after filter: `"Relevant: [N] files | Skipped: [N] files (logged to vault_skipped_files.log)"`

**Step 1.2b — Chunking Strategy (Industry Best Practice):**

All data is stored as **self-contained Q&A pairs** — each chunk is written so it carries full context about which company, role, and time period it refers to, making retrieval maximally precise.

**Chunk Format:**

```json
{
  "question": "What did you accomplish at Sprinklr as a Senior Product Analyst between Apr 2022 and Jul 2024?",
  "answer": "Built the Walmart Gen-AI support assistant handling 100K+ calls. Cut time-to-insight by 85% via LLM-based RCA engine. Scaled support efficiency 40% via unsupervised ML clustering.",
  "metadata": {
    "company": "Sprinklr",
    "role": "Senior Product Analyst",
    "duration": "Apr 2022 – Jul 2024",
    "impact_type": ["efficiency", "AI/ML", "scale"],
    "keywords": ["LLM", "GenAI", "support", "Walmart", "unsupervised ML"],
    "confidence": "high"
  }
}
```

**Chunk Types (one per signal):**

- `role_summary` — one chunk per job role (who, what, scope)
- `impact_bullet` — one chunk per measurable achievement
- `tech_stack` — one chunk listing all tools/tech used in that role
- `leadership` — one chunk for any people/stakeholder management story
- `academic_record` — one chunk per institution/exam
- `project` — one chunk per side project or voluntary work

**Chunking Parameters:**

- Chunk size: ~400 tokens
- Overlap: 80 tokens (ensures context continuity between adjacent chunks)
- Collection: `career_signals`
- Deduplication: check for existing chunk with same `(company, role, impact_type)` before inserting

**Confirmation Gate (Per Chunk):**
Before inserting each chunk, print:

```
📦 About to add to ChromaDB:
   Collection: career_signals
   Company: Sprinklr | Role: Senior Product Analyst
   Type: impact_bullet
   Content: "Built the Walmart Gen-AI support assistant..."

✅ Add this? (yes / rewrite / skip)
```

After full ingestion print summary:

```
✅ ChromaDB Ingestion Complete
   Total chunks added: [N]
   Collections updated: career_signals
   Total unique roles indexed: [N]
   Total unique companies: [N]
```

---

## EPIC 2: Base Template Setup

### Step 2.1 — Create `Base_Template.html`

Copy `Templates/CV Format.html` → `Templates/Base_Template.html`.

Replace all content with placeholder annotations:

```html
<!-- HEADER -->
<span class="name">{{FULL_NAME}}</span>
<span class="meta">| {{GENDER}} | {{AGE}}</span>

<!-- TAGBAR: 4 most relevant signal phrases for this company -->
<div class="t">{{TAGBAR_1}}</div>
<div class="t">{{TAGBAR_2}}</div>
<div class="t">{{TAGBAR_3}}</div>
<div class="t">{{TAGBAR_4}}</div>

<!-- Professional Summary: 3 lines, natural fill, 82-88 chars per line -->
<td class="dsc">{{PROFESSIONAL_SUMMARY}}</td>

<!-- Experience: .sub row per role, .dsc rows for bullets -->
<td class="tl">{{COMPANY_NAME}}</td>
<td>{{ROLE_TITLE}}</td>
<td>{{ROLE_TAG_1}} | {{ROLE_TAG_2}} | {{ROLE_TAG_3}}</td>
<td class="yr">{{DATE_START}} – {{DATE_END}}</td>
```

#### Locked CSS Guardrails (Never Change Here — Use `/edit-template`):

```css
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
.sub td:last-child,
.yr {
  white-space: nowrap;
}
--color-border: #000000;
body {
  font-family: "Segoe UI", Calibri, Arial, sans-serif;
  font-size: 9pt;
}
.sub {
  background: #f5f5f5;
  border-top: 2px solid #000;
  border-bottom: 1px solid #000;
}
```

> 🔒 Once created, `Base_Template.html` is **immutable**. Use `/edit-template` for any future changes.

**Bullet Character Limit Auto-Calibration:**

Immediately after the template is created, inject this JS snippet and open it in a browser. The script measures the actual pixel width of the `.dsc` column and stores the correct character limit:

```html
<!-- In Base_Template.html, inside <script> tag -->
<script>
  window.addEventListener("load", function () {
    const dscCell = document.querySelector("td.dsc");
    if (!dscCell) return;
    const pxWidth = dscCell.getBoundingClientRect().width;
    // Calibri/Segoe UI 9pt ≈ 5.8px avg char width
    const charLimit = Math.floor(pxWidth / 5.8);
    console.log("BULLET_CHAR_LIMIT:", charLimit);
    document.title = "CHAR_LIMIT: " + charLimit;
  });
</script>
```

Read the `BULLET_CHAR_LIMIT` value from the browser console, then store it as a locked comment in `Base_Template.html`:

```html
<!-- BULLET_CHAR_LIMIT: 44 -->
<!-- This value is auto-calibrated. Do not change manually. Re-run calibration after any CSS changes. -->
```

All Phase 6.7 bullet validation reads `BULLET_CHAR_LIMIT` from this comment — never the hardcoded 82–92 value.

---

## EPIC 3: GitHub Setup

### Step 3.1 — Connect GitHub

- Ask for GitHub Personal Access Token (repo scope) + repository URL
- Store in `.env` (gitignored)

### Step 3.2 — Initialize Sync Folder Structure

```
/                              ← repo root
├── Base_Template.html         ← LOCKED master template
├── README.md                  ← Master index with tree + GitHub Pages links (auto-updated)
├── Templates/
│   ├── CV Format.html         ← Original reference (never edited)
│   ├── Base_Template.html     ← Locked working template
│   └── TEMPLATE_CHANGELOG.md  ← Edit audit log
└── Sync/
    ├── <Company_A>/
    │   └── <Role_1>/
    │       ├── resume.html              ← Customized resume (GitHub Pages hosted)
    │       └── application_details.md  ← JD, score, live link, recruiter artifacts
    └── <Company_B>/
        └── <Role_1>/
            ├── resume.html
            └── application_details.md
```

### Step 3.3 — Auto-Generated README.md ⭐ NEW

A `README.md` at the repo root is created on first GitHub push and **auto-updated** after every new resume is added:

```markdown
# Sync — Resume Portfolio

> Powered by the Sync resume customization platform.

## Applications Dashboard

| #   | Company | Role              | Match Score | Resume                                                                       | Applied    |
| --- | ------- | ----------------- | ----------- | ---------------------------------------------------------------------------- | ---------- |
| 1   | Google  | PM – Search       | 94/100      | [View Resume](https://user.github.io/repo/Sync/Google/PM-Search/resume.html) | 2026-03-04 |
| 2   | Amazon  | Senior PM – Alexa | 88/100      | [View Resume](https://user.github.io/repo/Sync/Amazon/PM-Alexa/resume.html)  | —          |

## Folder Structure

Sync/
├── Google/
│ └── PM-Search/
│ ├── resume.html
│ └── application_details.md
└── Amazon/
└── PM-Alexa/
├── resume.html
└── application_details.md
```

---

## EPIC 4: JD Input & Data Acquisition

### Step 4.0 — Job Data Acquisition (Dual-Tier Strategy) ⭐ UPDATED

Before processing, the user acquires Job Descriptions via one of two modes. **Passive Stealth Mode is the default recommendation for safety.**

#### **Tier 1: Universal Manual Capture (Passive/Stealth) — DEFAULT**

- **Script:** `scripts/manual_capture.py`
- **Target:** **Any career portal** (Amazon, Google, startups, etc.).
- **Stability:** **PRODUCTION READY / ALWAYS SAFE.**
- **Mechanism:**
  - Passive network listener (`page.on('response')`).
  - Human drives the navigation and clicks (**Zero Automation Risk**).
  - Script logs `[JSON]` traffic and auto-saves relevant job payloads.
- **Outcome:** 100% reliable capture of whatever the user views on screen.

#### **Tier 2: Automated Capture (High-Speed) — [BETA]**

- **Script:** `scripts/microsoft_automation.py`
- **Target:** **Microsoft / Eightfold-powered portals** (expandable later).
- **Stability:** **EXPERIMENTAL.** Currently only stable for Microsoft.
- **Mechanism:**
  - Launch headful Playwright with stealth profile.
  - Automated pagination and pre-scrolling triggers to bypass lazy-loading.
- **Outcome:** Rapid extraction of 100+ jobs, but carries a higher risk of site-structure breakage or detection than Manual Mode.

#### **Step 4.0a — Unified CSV Export**

- **Format:** `data/<Company>_manual_jobs.csv`
- **Fields:** `Job Title`, `Job ID`, `Location`, `Description`, `Apply Link`.
- **Note:** `Experience` column is removed; extraction happens dynamically in Epic 6.

### Step 4.1 — Read Input CSV

File: `Input/job_batch.csv`

```csv
Company,Website,Role,JD
Google,https://google.com,PM - Search,"Full JD text..."
```

### Step 4.2 — JD Parsing → Hard/Soft Classification → Confidence Check

Parse the JD into a structured schema. **After parsing, immediately classify each requirement** using Claude:

```json
{
  "company": "Google",
  "role": "PM - Search",
  "required_skills": [
    { "skill": "AI/ML leadership", "skill_type": "Hard" },
    { "skill": "Search Ranking", "skill_type": "Hard" },
    { "skill": "Cross-functional execution", "skill_type": "Hard" },
    { "skill": "JIRA / Agile tooling", "skill_type": "Nice" },
    { "skill": "Voice UI experience", "skill_type": "Soft" }
  ],
  "required_metrics": ["DAU", "Latency", "Engagement"],
  "seniority_signals": ["cross-functional", "ambiguous environments"],
  "keyword_cluster": ["Agentic", "LLM", "Retrieval systems"]
}
```

**Classification prompt for Claude:**

> "For each JD requirement below, classify it as: Hard (candidate will be screened OUT without it), Soft (differentiates candidates but not a dealbreaker), or Nice (helpful but rarely assessed). Return as JSON with skill_type field."

Then query ChromaDB for top-8 signals and calculate **Context Confidence Score** (Hard skills only):

```
Confidence = (Hard skills with matching evidence) / (total Hard skills) × 100
```

> ⚠️ **Only Hard skills count toward the confidence gate.**
> Soft and Nice misses apply zero gate penalty (they still affect match score at tiered rates — see Epic 5).

- If **Confidence ≥ 90% on Hard skills** → proceed directly to Epic 5 (Confidence Gate)
- If **Confidence < 90% on Hard skills** → trigger **Gap Interview Loop** (Step 4.3)
- If gap is **uncoverable** (user has truly zero experience) → proceed with flag + strength penalty

### Step 4.3 — Gap Interview Loop (if Confidence < 90%)

> 🧠 Tone: Still warm and supportive — like a senior helping before an interview.
> ⏱️ **Max 3 questions per JD** — top-3 Hard skill gaps by JD keyword frequency only. All remaining gaps are written to `Input/gap_queue.md` with a -10 penalty pre-applied. The user can answer them asynchronously at any time.

For each of the top-3 gap skills, ask one targeted question:

```
I noticed this role at Google requires "Search Ranking experience" — I don't see anything about this
in your profile yet.

Have you ever worked with any kind of ranking, recommendation, or relevance system?
Even indirectly — like A/B testing content ordering, or building a feed algorithm?

(If yes, tell me the story. If no, that's okay — I'll help you handle it differently.)
```

**Three possible outcomes per gap:**

1. **User provides story** → extract structured signal, store in Obsidian + ChromaDB, update confidence score
2. **User says "I have no experience"** → flag as confirmed gap, suggest theoretical prep:

   ```
   No worries! Here are 3 questions you might get asked about Search Ranking:
   1. "How would you prioritize ranking signals for a search feature?"
   2. "Walk me through how you'd A/B test a ranking algorithm change."
   3. "How do you balance freshness vs relevance in search?"

   Would you like me to wait while you note these down? Once you've prepared answers,
   you can share them here and I'll add them to your profile. Or type 'skip' to continue.
   ```

3. **User skips** → proceed but apply -10 pts to match score per unresolved Hard gap

**Remaining gaps (beyond top-3)** are auto-written to `Input/gap_queue.md`:

```
📋 Gap Queue — Google PM - Search

4. No evidence of: "JIRA / Agile tooling" (Soft — penalty: 0 pts)
5. No evidence of: "Voice UI experience" (Soft — penalty: 0 pts)

Answer any of these later to improve your profile for future applications.
```

After the 3-question loop:

```
Updated Confidence Score: [X]% (Hard skills only)
Deferred to gap_queue.md: [N] gaps
→ Unresolved Hard gaps reduce your Application Strength Score.
Proceed to Epic 5 confidence gate? (yes/no)
```

### Step 4.4 — ChromaDB Retrieval (PM-SYNC-13)

After confidence gate passes, query ChromaDB → top-8 most relevant signal entries for this JD.

**Retrieval Spot-Check (mandatory before Phase 6.2):**

Before any content is drafted, show the retrieved signals to the user:

```
🔍 Retrieval Spot-Check — Google PM - Search

I will build your resume from these 8 experience signals:

1. [Amex] Spearheaded AML scoring model handling 30M+ daily txns...
2. [Sprinklr] Led Walmart Gen-AI support assistant (100K+ calls)...
3. [Sprinklr] Unsupervised ML clustering reduced support tickets 40%...
4. ...

Do these feel highly relevant to this role? (confirm / replace [N] / re-rank)
```

- User confirms → proceed to Epic 5
- User replaces → run a new ChromaDB query with updated keywords, re-show
- User re-ranks → reorder signals by relevance, proceed

No resume is drafted until signals are confirmed.

---

## EPIC 5: Pre-Customization Confidence Gate ⭐ NEW EPIC

> This is a mandatory checkpoint BEFORE any resume content is written.

### Step 5.1 — Generate Confidence Report

For each JD required skill:

```
✅ AI/ML leadership          → Covered (Amex, Sprinklr — 3 strong bullets)
✅ Cross-functional execution → Covered (Amex — 18-member scrum team)
⚠️  Search Ranking            → Partial (user gave indirect story — medium confidence)
❌  Voice UI / Conversational → Missing (no experience, prep questions given)
```

### Step 5.2 — Application Strength Score (Pre-Resume)

```
Application Strength: 78/100
──────────────────────────────
Skill coverage:      +52 pts (6/8 JD skills covered)
Metric alignment:    +16 pts (4 matching KPI types)
Tagbar fit:          +10 pts (all 4 tagbar slots map to JD)
Penalties:
  Hard miss (Voice UI):    -10 pts  ← unresolved Hard gap
  Soft miss (Voice UX):      0 pts  ← Soft gaps never penalized
  Prep given (Search Rank): -5 pts  ← partial credit (theoretical prep provided)
──────────────────────────────
Final: 63/100 | Target: ≥90/100 for a strong application
```

**Penalty Tiers:**
| Gap Type | Evidence | Penalty |
|----------|----------|---------|
| Hard skill | No experience, no prep | -10 pts |
| Hard skill | Theoretical prep given | -5 pts |
| Soft skill | Any gap | 0 pts |
| Nice-to-have | Any gap | 0 pts |

### Step 5.3 — Gate Decision (With Override)

The gate **never blocks** — it informs. All scores display the same 3 options:

```
Application Strength: 63/100

Options:
  [A] Continue anyway  — proceed with current signals
  [B] Answer gap questions — run more gap interview loops
  [C] Skip this role  — move to next CSV row

Note: If Override=true in job_batch.csv, gate is bypassed automatically.
```

- Score ≥ 90% → Auto-proceed with confirmation
- Score 75–89% → Show options, recommend [A] or [B]
- Score < 75% → Show options, recommend [B] first, warn that [A] produces a weaker application

**CSV Override Flag:**
Add an `Override` column to `Input/job_batch.csv` for batch runs:

```csv
Company,Website,Role,JD,Override
Google,https://google.com,PM - Search,"JD text...",false
Amex,https://amex.com,Senior PM,"JD text...",true
```

When `Override=true`, the gate step is skipped entirely and the system proceeds to Epic 6 at whatever score it has.

---

## EPIC 6: Resume Customization Engine (Per Application)

> Every phase is an atomic `bd` task. Each must be verified before the next begins.

### Phase 6.1 — Intelligence Map

Create `Sync/<Company>/<Role>/intelligence_map.md`:

- Map JD skills → experience evidence from ChromaDB signal pool
- Define 4 Tagbar phrases
- Write Top-Third Marketing Pitch for this company

### Phase 6.2 — Content Draft

Draft full content in `Sync/<Company>/<Role>/content_draft.md`:

**Non-Negotiable Rules:**

| Rule                | Standard                                                            |
| ------------------- | ------------------------------------------------------------------- |
| Bullet format       | Google XYZ: "Accomplished [X] as measured by [Y] by doing [Z]"      |
| Character count     | Read from `<!-- BULLET_CHAR_LIMIT: N -->` in Base_Template.html     |
| Line count          | Exactly 1 line per bullet — zero wrapping                           |
| Bold keywords       | 2–4 bold terms per bullet                                           |
| Metric density      | At least 1 number/% per bullet                                      |
| Fabrication rule    | NEVER invent metrics — verified signal pool only                    |
| Trailing adjustment | Max 10 `&nbsp;` for micro gaps (<3mm). Rephrase for major gaps.     |
| Sub-header tags     | Max 20 chars per tag phrase (3 × 20 + 2 pipes fits safely in `.c4`) |

### Phase 6.3 — Brand Research (with Registry + Fallback)

**Step 1 — Check `brand_colors.json` registry first:**

```python
import json
registry = json.load(open('brand_colors.json'))
colors = registry.get(company_name.lower())
if colors:
    primary, secondary, accent = colors['primary'], colors['secondary'], colors['accent']
else:
    # Step 2: Web search for official brand colors
    # search: "<company> official brand colors hex code"
    # If not found: Step 3 — use neutral premium fallback
    primary, secondary, accent = '#1a1a2e', '#16213e', '#0f3460'
```

Map to CSS variables:

```css
--color-primary: #HEX; /* Primary brand color → section headers */
--color-secondary: #HEX; /* Secondary → tagbar background */
--color-accent: #HEX; /* CTA / link color */
```

### Phase 6.4 — HTML Assembly

1. `cp Templates/Base_Template.html Sync/<Company>/<Role>/resume.html`
2. Inject all content from `content_draft.md`
3. Apply brand color CSS variables

### Phase 6.5 — Sub-Header Visual Styling

Pipe-separated, light background `.sub` rows only:

```css
.sub {
  background: #f5f5f5;
  color: #111;
  border-top: 2px solid #000;
  border-bottom: 1px solid #000;
}
```

Format: `Company | Role Title | Tag1 | Tag2 | Tag3 | Date`

> ✅ Tag enforcement: Each of Tag1, Tag2, Tag3 must be **≤ 20 characters** including spaces. Validate at Phase 6.2 draft stage before assembly.

### Phase 6.6 — Date Column Validation (HARD STOP)

- Assert `.c5 ≥ 14.5%`
- Assert `white-space: nowrap` on `.yr` and `.sub td:last-child`
- If clipping → increase `.c5` to `16%`, reduce `.c2` + `.c4` by `0.75%` each

### Phase 6.7 — Bullet Line Validation (HARD STOP)

- Read `BULLET_CHAR_LIMIT` from `<!-- BULLET_CHAR_LIMIT: N -->` in the HTML comment
- Run char count on each `<li>` using `BULLET_CHAR_LIMIT` as the target (not hardcoded 82–92)
- Apply `text-align-last: justify` on `.dsc li` to auto-snap bullets to right margin
- Apply `stretch-1` class for bullets in the 75% threshold range
- Rephrase (add genuine context) for bullets significantly under budget
- Trim lowest-value words for bullets over budget
- Assert zero `<br>` inside any `<li>`

### Phase 6.8 — Compression Pass + Puppeteer Validation

```bash
npx puppeteer@latest node -e "
const puppeteer = require('puppeteer');
async function validate() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.setViewport({ width: 794, height: 1123 });
  await page.goto('file://' + process.argv[2]);
  const height = await page.evaluate(() => document.body.scrollHeight);
  const overflows = height > 1123;
  console.log(overflows ? 'OVERFLOW: ' + height + 'px > 1123px' : 'OK: fits 1 page');
  await browser.close();
}
validate();
" -- Sync/<Company>/<Role>/resume.html
```

- If `OVERFLOW` → reduce spacer heights (6px → 4px), reduce `.dsc` line-height (1.35 → 1.28), re-run
- If content too short → increase spacers or font-size by 0.5pt steps
- Repeat until Puppeteer reports `OK: fits 1 page`
- Save `validation_report.json` with timestamp and final height to `Sync/<Company>/<Role>/`

### Phase 6.9 — Match Score Calculation

- +10 pts per JD Hard keyword present in resume
- +5 pts per JD Soft keyword present in resume
- +5 pts per matching metric type
- +5 pts if all 4 tagbar slots map to JD signals
- Hard miss (no prep): -10 pts | Hard miss (prep given): -5 pts
- Soft miss: 0 pts | Nice-to-have miss: 0 pts
- Cap at 100. Target: ≥90/100.

### Phase 6.10 — GitHub Push + Version Control + GH Pages

**Step A — Version Copy (FIX-13):**
Before overwriting any existing `resume.html`, copy it to a versions archive:

```bash
mkdir -p Sync/<Company>/<Role>/versions
cp Sync/<Company>/<Role>/resume.html Sync/<Company>/<Role>/versions/resume_$(date +%Y-%m-%d).html
```

**Step B — Commit with descriptive message:**

```bash
git add Sync/<Company>/<Role>/
git commit -m "feat: <Company> - <Role> resume (score: XX/100)"
git push sync main
```

**Step C — Poll GitHub Pages before writing live URL (FIX-10):**

```bash
# Poll until status = "built" or timeout at 5 min
for i in $(seq 1 30); do
  STATUS=$(curl -s -H "Authorization: token $GH_TOKEN" \
    https://api.github.com/repos/$REPO/pages/builds/latest | python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")
  if [ "$STATUS" = "built" ]; then echo "Pages live"; break; fi
  echo "Waiting ($i/30)..."; sleep 10
done
```

Only write the `https://` URL to `application_details.md` **after** `status = "built"`.
If timeout → write `[⏳ Building — check in 2 min](https://url)` as placeholder.

**Step D — Idempotent README regeneration (FIX-08):**

```bash
# Regenerate README.md from scratch using all application_details.md files
python3 - <<'EOF'
import os, re
rows = []
for root, dirs, files in os.walk('Sync'):
    for f in files:
        if f == 'application_details.md':
            content = open(os.path.join(root,f)).read()
            company = os.path.basename(os.path.dirname(root))
            role = os.path.basename(root)
            score = re.search(r'Match Score: (\d+)/100', content)
            url = re.search(r'https://[^\s)]+resume\.html', content)
            rows.append((company, role,
                score.group(1)+'/100' if score else '?',
                f'[View]({url.group(0)})' if url else 'Building...'))
header = '# Sync — Resume Portfolio\n\n| # | Company | Role | Score | Resume |\n|---|---------|------|-------|--------|\n'
table = ''.join(f'| {i+1} | {r[0]} | {r[1]} | {r[2]} | {r[3]} |\n' for i,r in enumerate(rows))
open('README.md','w').write(header + table)
print(f'README updated: {len(rows)} applications')
EOF
git add README.md
git commit -m "docs: regenerate README dashboard"
git push sync main
```

Create `Sync/<Company>/<Role>/application_details.md`:

```markdown
# Application: <Company> — <Role>

## Match Score: XX/100 | Application Strength: XX/100

**Target: ≥90/100**

## GitHub Pages Live Link

https://<username>.github.io/<repo>/Sync/<Company>/<Role>/resume.html

## Key JD Requirements

| Requirement    | Coverage   | Confidence |
| -------------- | ---------- | ---------- |
| AI/ML          | ✅ Strong  | High       |
| Search Ranking | ⚠️ Partial | Medium     |
| Voice UI       | ❌ Missing | —          |

## Full Job Description

<paste JD here>
```

### Phase 6.11 — Recruiter Artifacts

**InMail (≤300 words):**

```
Hi [Name],
I came across the [Role] at [Company] and the alignment with my background feels very direct.
I've spent [X years] at [Companies], where I [1 sharp XYZ credential relevant to this JD].
For [Company] specifically, I see a direct fit: [1 sentence connecting your strongest signal to their JD].
My tailored resume is live here: [GitHub Pages Link]
Would love to connect for 15 minutes.
[Your Name]
```

**LinkedIn Connect (≤300 characters HARD LIMIT):**

```
Hi [Name], applying to [Role] at [Company]. My [1 crisp signal] aligns directly. [GitHub Pages link]. Would love to connect!
```

---

## EPIC 7: Loop Control + Session Exit

After completing Phases 6.1–6.11 for one row:

- Mark all subtasks closed in `bd`
- Run `bd sync`
- Prompt: "✅ [Company] - [Role] done. Score: XX/100. Next application? (yes/no)"
- If yes → next CSV row, restart from Epic 4.1
- If no → `git push`, save state, exit

---

## EPIC 7: Continuous Automation (GitHub Actions) ⭐ NEW

GitHub Actions serves as the engine that keeps the Sync platform "alive" without manual intervention.

### Step 7.1 — Resume Generation Workflow

**File:** `.github/workflows/resume-generation.yml`

- **When it helps:** Whenever `data/` (job batches) or `templates/` (design) change.
- **What it does:** Sets up a Python environment, runs `core_engine/build_final_batch.py`, and bundles the resulting HTML/PDF files as an Action Artifact.
- **Benefit:** Decouples generation from your local machine.

### Step 7.2 — Auto-Deployment Workflow

**File:** `.github/workflows/deploy-portfolio.yml`

- **When it helps:** Runs automatically after a successful Resume Generation.
- **What it does:** Downloads the generated resumes and pushes them to the `gh-pages` branch.
- **Benefit:** Your live portfolio URL (GitHub Pages) is always up to date with zero manual `git push` commands.

### Step 7.3 — Job Scraper Cron

**File:** `.github/workflows/job-scraper-cron.yml`

- **When it helps:** Scheduled to run every day (e.g., 4 AM UTC).
- **What it does:** Executes scrapers to find new jobs and commits them to the `main` branch.
- **Benefit:** You wake up to a fresh list of jobs in your `data/` folder every morning.

### Step 7.4 — CI-Compatible Paths

All scripts in `core_engine/` must use `os.path.dirname(os.path.abspath(__file__))` to resolve paths relative to the repository root, ensuring they run identically on Mac (local) and Ubuntu (GitHub).

### Step 7.5 — Real-Life User Journeys

#### **Case 1: Data-Driven Evolution (The "New Application" Loop)**

- **Situation:** You find a "GenAI PM" role at Google.
- **Action:** You update `data/final_job_batch.csv` with the new JD.
- **Automation:** GitHub Actions notices the change → Runs Python engine specifically for the new row → Generates `Sync/Google/GenAI_PM/resume.html` → Updates the Dashboard.
- **Result:** You get a live link to send to the recruiter without touching your terminal.

#### **Case 2: Design-Driven Evolution (The "Brand Update")**

- **Situation:** You decide that "Inter" font looks better than "Calibri".
- **Action:** You edit `templates/CV Format.html`.
- **Automation:** GitHub Actions triggers → Re-runs the build for **all** your current applications (Google, Amazon, etc.) using the new font.
- **Result:** All your live links are instantly updated with the current design, ensuring brand consistency across all active applications.

### Step 7.6 — Scraper Architecture & Safety (Anti-Ban)

The system uses a **Hybrid Scraper Logic** to manage the trade-off between effort and safety.

1.  **Discovery (Automated Cron):** Runs daily on GitHub Actions to find _links_ to new job postings. Use for open, non-auth portals.
2.  **Extraction (Manual Stealth Mode):** For high-risk portals (FAANG/Workday), use `manual_capture.py` locally. You browse normally; the script "ghosts" your network traffic to extract the JD.
3.  **The Effort Factor:** Even if extraction is manual, the **Discovery** is automated. You only spend effort on jobs that actually matter, while the system keeps the pipeline full in the background.

---

## EPIC 8: Future Artifacts (Queued for Later)

| Artifact                                    | Status                |
| ------------------------------------------- | --------------------- |
| "Why Me" Slide Deck (Claude frontend skill) | Queued                |
| LinkedIn narrative engine                   | Roadmap (3–6 months)  |
| Interview simulation (voice-based)          | Roadmap (6–12 months) |
| Hosted SaaS version                         | Roadmap (12+ months)  |

---

## GUARDRAILS (Always Active — Every Session)

| #   | Rule                                                                    |
| --- | ----------------------------------------------------------------------- |
| 1   | Never fabricate metrics — verified signal pool or user interview only   |
| 2   | `Base_Template.html` is immutable — only `/edit-template` can change it |
| 3   | Max 10 `&nbsp;` for micro text gaps — rephrase for major gaps           |
| 4   | Date column `.c5 ≥ 14.5%` — never reduce below this                     |
| 5   | `white-space: nowrap` on all date cells — absolute                      |
| 6   | 82–92 char target per bullet — validate with char count                 |
| 7   | 1 page only — hard stop, no exceptions                                  |
| 8   | XYZ formula on every bullet — Accomplished X measured by Y by doing Z   |
| 9   | Border color: `#000000` only — no gray borders                          |
| 10  | Sub-header: pipe approach — no heavy dark backgrounds                   |
| 11  | ChromaDB confirmation gate before each chunk insert                     |
| 12  | ≥90% Confidence Score required before Epic 6 starts                     |
| 13  | Gap penalties propagate directly to Application Strength Score          |
| 14  | README.md is auto-updated after every new GitHub push                   |
| 15  | New signals from gap interviews must be saved to Obsidian + ChromaDB    |

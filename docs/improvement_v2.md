# Sync Platform Improvements & Post-Mortem V2

This document captures a comprehensive adverse review of the Sync Resume Customization pipeline, detailing both architectural flaws and execution failures encountered during the latest run. The focus is strictly on why existing systems broke down and how they must be redesigned for the next iteration.

---

## 1. The Rectangular Block Failure & A4 Dimension Rigidity

The current system failed to achieve a perfect "Rectangular Block" fit on a standard A4 page (210mm x 297mm). The approach of aggressively computing bullet length (`BULLET_CHAR_LIMIT`) or blindly injecting `font-size: 7pt` CSS strings proved extremely brittle. The difference between a browser's infinity-scroll height and a rigorous PDF Print Preview boundary was fundamentally misunderstood by the system engine.

### Improvement Steps

- **Embrace the Container Query:** The HTML resume MUST be constrained to a hard 8.5in or 210mm width natively in CSS, not by manually adjusting character limits across the board.
- **Character Budgeting:** Instead of a global ~85 character limit, the system needs column-specific math. If the description cell takes up 75% of the page width, the character budget must be explicitly defined (e.g., 82-88 characters for Calibri 10pt) for _that specific cell_.
- **The "5% Stretch Strategy":** We must use `text-align-last: justify; white-space: nowrap;` so that once a bullet hits 95% of its character length budget, the browser mathematically stretches the remaining air. We failed to leverage this CSS property in the automation loop.
- **Failures in Automated Validation:** The `puppeteer` script responsible for measuring A4 overflow catastrophically failed due to dependency and timeout issues, forcing a complete fallback to manual CSS adjustments. Future validation endpoints need decoupled execution environments independent of local Chromium instability.

## 2. Context Loss in Vector DB Chunking (ChromaDB)

The resume generation pipeline currently hallucinates or loses project context because the initial signal ingestion is flawed. When chunking text for the vector database, the context of _which_ project the signal belongs to (e.g., Walmart Spark, Qatari PM, Amex Risk) was disconnected from the granular trait (e.g., "Product Vision" or "Cross-functional Leadership").

### Improvement Steps

- **Hierarchical Metadata Tagging:** Every chunk embedded into ChromaDB MUST contain explicitly hardcoded metadata tags of its parent context. Example: `{"company": "Sprinklr", "project": "Sharek (Qatari PM)", "category": "Computer Vision"}`.
- **Retrieval-Augmented Windowing:** When the LLM runs a query like "Find examples of Product Strategy", the retrieval engine must pull the _surrounding_ contextual chunks to ensure the drafted bullet seamlessly, and correctly, references the true underlying project, eliminating context cross-contamination.

## 3. Persistent Memory vs. Docker Overhead

In an attempt to spin up ChromaDB, the system incorrectly defaulted to spinning up Docker containers and volumes rather than utilizing localized, persistent storage. This introduced unnecessary dependencies, network overhead, and complexity for a local terminal application.

### Improvement Steps

- **Strictly Local Persistent Storage:** The ChromaDB client must be initialized explicitly pointing to a local directory (e.g., `chromadb.PersistentClient(path="/Users/.../.chroma_db")`) mapped inside the Sync project folder. Docker containers must not be used for local, single-user script execution.

## 4. Logical Bullet Point Distribution

The current automation blindly enforces a flat number of bullet points per role, which violates standard resume reading psychology and unnecessarily bloats page height. The primary/current role was treated with the same depth as a voluntary role from earlier in the career.

### Improvement Steps

- **Temporal Weighting Algorithm:** The engine must be programmed with an optimal upper limit (e.g., 9-10 bullets max to consistently fit the A4 page height) distributed across an exponential decay curve.
  - **Current Role (American Express):** 4 to 5 highly detailed bullets.
  - **Previous Role (Sprinklr):** 3 bullets.
  - **Older/Voluntary Roles (Sukha):** 1-2 bullets max.
- **Granular Priority:** Only the hard JD keywords with $>90\%$ match relevance should be allocated to the most recent role's bullet allocation. Older roles should fill auxiliary (Soft) keywords.

## 5. GitHub Pages Deployment & Branch Isolation Failures

The system attempted to push the active working directory directly to GitHub to host the resumes via GitHub Pages. The URLs generated did not resolve correctly, resulting in broken live links.

### Improvement Steps

- **Branch Isolation:** The compiled HTML resumes and recruiter artifacts must be strictly isolated into a clean, dedicated branch (e.g., `gh-pages` or a deployment folder configuration) entirely separate from the `main` source code.
- **GitHub Actions / Static HTML:** Use automated GitHub Actions to build and deploy the static HTML from this isolated branch to GitHub Pages, ensuring the routing properly resolves to the expected URLs without conflating repository structure with site architecture.

## 6. "Dumb" String Matching for Match Scores

The plan explicitly touted an "AI-powered signal engineering" platform, but the Match Score calculation (Phase 10) was executed using a rudimentary Python script doing basic substring matching (`kw.lower() in html`).

- **Improvement:** Introduce Semantic LLM matching. If the JD asks for "Generative AI" and the resume says "Gen-AI", it should correctly identify the match. The rigid substring check forced unnatural "keyword weaving" at the end of the pipeline.

## 7. Task Management (`bd` CLI) Desynchronization

The core directive insists on using the `bd` (Beads) CLI for all state synchronization.

- **Improvement:** Automation loops must securely map and fetch valid `bd` issue IDs before attempting status updates. Blindly sending commands like `bd close 37` or using deprecated commands like `bd context` broke the execution flow.

## 8. The "Dual-Tier" Scraper Pivot

The Epic 4 data acquisition plan pivoted heavily to a manual "Passive Capture" mode because the automated headless/headful scraping of complex UI portals (like Microsoft's Eightfold) failed due to obfuscation and dynamic rendering.

- **Improvement:** The extraction engine must be rebuilt natively into browser extensions or deeply integrated with DevTools (Network tab monitoring) rather than relying on brittle DOM-traversal scripts that instantly fail upon interface updates.

## 9. Inconsistent Confidence Gates

The architecture requires a strict `≥ 90%` Confidence Gate _before_ generating the HTML.

- **Improvement:** In execution, the engine eagerly skipped straight to generating the HTML drafts and compiling the templates before explicitly resolving the gap queues with the user. The pipeline must insert hard programmatic breakpoints that require human validation input before allowing the generation chain to proceed.

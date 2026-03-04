# SYNC — MVP PRODUCT REQUIREMENTS DOCUMENT (PRD)

---

# 1. EXECUTIVE SUMMARY

## Problem Definition

Early-to-mid career Product Managers (4–8 years experience) in India fail to secure interview opportunities due to weak, fragmented, and misaligned professional signal across resume and recruiter outreach.

### Current Baseline (Primary Persona)

- <1% shortlist rate
- 0–1 recruiter inbound per month
- <20 low-quality applications per month due to high manual effort
- No structured JD-alignment workflow

### MVP Target Transformation

- Enable generation of up to ~100 high-quality, JD-customized applications per month
- Sustain ≥5% shortlist rate (validation goal)
- Reduce customization effort to <15 minutes per application

This MVP focuses on proving that structured signal modeling + semantic retrieval + JD-aware resume optimization can measurably improve shortlist conversion.

---

## Core Value Proposition (MVP Scope)

Sync is a signal engineering system.

It converts raw experience into a structured, retrievable professional memory layer and activates it through JD-aligned resume optimization.

This MVP remains power-user oriented and Claude Code–orchestrated.

---

## North Star Metric (MVP)

Interview Conversion Rate = Interviews Secured / Applications Submitted

### Supporting Validation Metrics

- High-Quality JD-Customized Applications per Month (Target: up to 100)
- JD Alignment Score uplift ≥20%
- Time per Customized Application <15 minutes

---

## 2.5 Secondary Goals (MVP+)

- **Hybrid Job Extraction**: Enable power users to dynamically "learn" and scrape specific corporate career portals (Google, Amazon, etc.) via headful automation.
- **Optional Batch Input**: Support both manual CSV ingestion and automated scraper output.

---

## Explicit Non-Goals (MVP)

- No automated mass apply
- No recruiter marketplace
- No hosted SaaS deployment
- No advanced interview simulation

---

# 2. PRIMARY PERSONA — TITLE-MISMATCH PM

## Snapshot

- ~4 years experience
- ₹30 LPA
- Performs PM responsibilities without official PM title
- Aspires to FAANG-tier / global SaaS PM role

## Current Behavior

- <20 manual applications/month
- Resume manually edited each time
- Generic outreach messages
- Spreadsheet tracking

## Desired State After MVP Adoption

- Structured signal capture
- Semantic retrieval of relevant impact per JD
- Dedicated ResumeVersion per job
- Efficient JD customization workflow
- Clear shortlist tracking dashboard

---

# 3. MVP USER JOURNEYS

---

## JOURNEY 1 — Career Signal Capture + Indexing

### Trigger

User logs work reflections via UI.

### Flow

1. User pastes reflection.
2. Claude extracts structured signal (metrics, ownership, scope).
3. JSON validated and stored in MongoDB.
4. Reflection embedded and stored in Chroma vector DB.

### State Transition

Idle → Signal Stored → Signal Indexed

### Success Criteria

Signal retrievable via semantic query.

---

## JOURNEY 2 — JD-Based Resume Optimization (Core MVP Journey)

### Trigger

User pastes Job Description.

### Preconditions

- Base resume uploaded
- Signal entries exist

### Flow

1. Claude parses JD into structured schema.
2. JD embedded and queried against Chroma.
3. Top-k semantically relevant signal entries retrieved.
4. Resume loaded.
5. Claude generates optimization plan using:
   - JD schema
   - Retrieved signal entries
6. Bullets rewritten under constraints:
   - Must visually fit within a single rendered line
   - Layout validated after compilation
   - No fabricated metrics
7. Deterministic layout validation:
   - Detect line overflow
   - Detect >1 page (hard stop)
   - Auto-rewrite if needed
8. New ResumeVersion created in MongoDB.

### State Transition

Resume Draft → JD Parsed → Signal Retrieved → Rewritten → Layout Validated → ResumeVersion Stored

### Success Criteria

- PDF compiles to exactly one page
- Alignment score improves ≥20%

---

## JOURNEY 3 — Application Logging

### Trigger

User applies to a role.

### Flow

1. ResumeVersion selected.
2. ApplicationRecord created in MongoDB.
3. Status updated over time.

### Success Criteria

Shortlist rate measurable and attributable to ResumeVersion.

---

# 4. MVP MODULES

## 4.1 Career Signal Modeling Engine

Responsibilities:

- Extract structured signal
- Persist to MongoDB
- Generate embeddings
- Store in Chroma

Deterministic:

- Schema validation
- Embedding storage confirmation

---

## 4.2 Chroma Retrieval Engine (New MVP Component)

Infrastructure:

- Chroma vector DB running via Docker
- Accessed through Docker MCP from Claude Code CLI

Responsibilities:

- Store embeddings
- Retrieve top-k relevant signal entries per JD

Purpose:
Improve precision of resume rewriting by grounding Claude in relevant experience.

---

## 4.3 JD Parsing Engine

Model: Claude (via Claude Code CLI)

Outputs structured requirement schema.

---

## 4.4 Resume Optimization Engine

Model: Claude (primary reasoning engine)

Inputs:

- JD schema
- Retrieved signal entries
- Base resume

Validation Layer:

- Render-width enforcement
- Line overflow detection
- One-page enforcement
- Auto-iteration loop

---

## 4.5 ResumeVersion Manager

Each JD → one immutable ResumeVersion.
Stored in MongoDB with metadata.

---

## 4.6 Application Tracker

Tracks linkage between:

- JD
- ResumeVersion
- Outcome

Outputs shortlist rate.

---

# 5. DATA ARCHITECTURE (MVP)

## MongoDB (Source of Truth)

Collections:

1. users
2. career_signal_entries
3. jd_profiles
4. resume_versions
5. application_records

## Chroma (Semantic Layer)

Stores:

- Embeddings of signal entries
- Optional embeddings of resume bullets

MongoDB = structured truth
Chroma = semantic retrieval layer

---

# 6. ORCHESTRATION MODEL (MVP)

Primary Orchestrator:
Claude Code CLI

Tooling:

- MongoDB (via local connection)
- Chroma (via Docker MCP)
- Local LaTeX compile + validation scripts

Claude responsibilities:

- Parse JD
- Trigger Chroma retrieval
- Generate rewrite
- Validate structured outputs

No additional paid API integrations beyond existing Claude access.

---

# 7. NON-FUNCTIONAL REQUIREMENTS (MVP)

Latency Targets:

- JD parsing <5s
- Retrieval <2s
- Resume optimization <20s

Cost Target:
Zero additional API cost beyond Claude access.

Reliability:

- Layout validation deterministic
- Retrieval must always return top-k results (fallback: full context load)

Security:

- All data stored locally
- Chroma runs in local Docker container

---

# 8. METRICS (MVP VALIDATION)

North Star:
Interview Conversion Rate

Supporting KPIs:

- Applications Submitted per Month (target: scale to ~100)
- JD Alignment Score uplift ≥20%
- Time per application <15 min
- Recruiter inbound count

---

# 9. KEY MVP RISKS

1. Docker MCP integration complexity
2. Embedding quality affecting retrieval relevance
3. Claude output variability under constraint

Mitigation:

- Simple embedding model initially
- Fallback to full-context mode
- Deterministic validation scripts

---

# 10. MVP BUILD PLAN

Sprint 1:

- MongoDB setup
- Signal ingestion
- Chroma Docker setup
- Embedding + retrieval pipeline

Sprint 2:

- Resume rewrite with retrieval grounding
- Layout validation engine
- ResumeVersion manager

Sprint 3:

- Application tracker
- Metrics dashboard

---

# MVP EXECUTION SUMMARY

This MVP integrates Chroma as a lightweight semantic retrieval layer via Docker MCP while keeping MongoDB as the structured source of truth and Claude Code CLI as the orchestrator.

It validates whether grounding resume optimization in semantically retrieved impact improves shortlist conversion while enabling scalable high-quality application volume.

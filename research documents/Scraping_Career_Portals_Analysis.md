# Scraping Career Portals Analysis & Knowledge Base

This document tracks the common patterns, failure points, and robust solutions found while automating different career portals. It serves as the long-term memory for the `discovery_engine.py`.

---

## 🏗️ System Patterns

### 1. Eightfold.ai (Microsoft, etc.)

- **Signature**: Presence of classes like `cardContainer-*`, `pagination-module_*`, or API calls to `/api/pcsx/`.
- **Learnings**:
  - **Dynamic Selection**: Job cards use randomized suffixes (e.g., `cardContainer-GcY1a`). Selectors should use partial matches or specific container roles.
  - **Lazy Loading**: Columns are often rendered as the user scrolls. A full `scrollTo` is required before DOM analysis.
  - **DOM Volatility**: Elements detach frequently during pagination. Requires aggressive `scroll_into_view` and `try-except` wrappers.
- **Robust Selectors**:
  - Job Cards: `.card-F1ebU, .cardContainer-GcY1a, [role="listitem"]`
  - Next Button: `button[aria-label*='Next'], [data-automation-id='next-button']`

---

## ❌ Known Failures & Solutions

### Error: `TimeoutError: Page.wait_for_selector exceeded`

- **Context**: Microsoft Portal Page 1.
- **Root Cause**: Selector `li[id^="job-card-"]` was too specific and didn't match the Eightfold `div` structure.
- **Solution**: Use broader container classes identified via class frequency analysis.

### Error: `ElementHandle.scroll_into_view_if_needed: Element is not attached to the DOM`

- **Context**: Clicking through a long list of cards.
- **Root Cause**: React/Vue rendering engine recycling list items (Virtual Scrolling).
- **Solution**: Re-query the element list if stale, or skip detached elements and rely on the next iteration/scroll.

---

## 🛠️ Reusable Logic (Future-Proofing)

- **Lazy Load Trigger**: `await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")`
- **Session Takeover**: AlwaysEstablish session manually via `input("start")` to bypass complex Auth/Bot detection.

### [Microsoft] Learning Case (2026-03-04 06:42:15)
- **Error**: Lazy loading blocks card extraction
- **Solution**: Implement pre-scroll using scrollTo(0, scrollHeight) before wait_for_selector

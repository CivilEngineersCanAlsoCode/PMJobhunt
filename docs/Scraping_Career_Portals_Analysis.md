# Research Analysis: Scraping Job Portals (Strict No-Ban Constraints)

**Goal:** Extract PM job descriptions from Top 10 Tier companies (Google, Microsoft, Amazon, Meta, etc.) relying only on safe, invisible, or strictly keyboard-navigated automation to completely avoid IP bans.

---

## 1. Direct HTTP Parsing (`read_url_content` / cURL)

- **Approach:** Sending standard HTTP GET requests to the career search URLs without any JavaScript rendering or browser automation.
- **Result:** **Massive Success for Google.** Failed for others.
- **Analysis:** Google builds their career page with incredible SEO and accessibility in mind. They embed the actual job data directly into the raw HTML. Zero ban risk, executes in milliseconds. However, Microsoft, Amazon, Meta, Adobe, and Salesforce send back empty HTML "shells" and require heavy client-side JavaScript to load the jobs.

## 2. Browser Automation with Keyboard-Only Constraints (Playwright / Puppeteer)

- **Approach:** Launched headless Chromium. Forbade mouse clicks and forced the use of only `Tab` and `Shift+Tab` to simulate an accessibility tester or visually impaired user.
- **Result:** **Failed (Keyboard Traps).**
- **Analysis:** Blind tabbing is incredibly brittle on modern web apps. The `Tab` sequence gets infinitely stuck inside invisible accessibility helper navigation bars, Shadow DOM elements, or mandatory cookie-consent modals that trap focus.

## 3. DOM Target Focus + Keyboard Enter

- **Approach:** Refined the browser script to search the DOM for the exact `href` of the job, jump the keyboard focus directly to that element using `.focus()`, and then press `Enter`.
- **Result:** **Failed (JS Routing Events).**
- **Analysis:** Amazon and Microsoft use complex Single Page Application (SPA) routers (like React/Angular). Pressing `Enter` on an `<a>` tag often doesn't trigger the page transition because they explicitly listen for `onClick` mouse events, instead of native keyboard `Enter` events on those custom elements.

## 4. Direct Backend API Querying (Python Requests)

- **Approach:** Bypassed the UI entirely. Inspected the network traffic to find the hidden backend JSON APIs that the frontends use, and wrote Python scripts to hit them directly.
- **Result:** **Failed (Anti-Bot Defenses).**
- **Analysis:**
  - **Microsoft:** Returned a `502 Bad Gateway` error, which happens when their web-application firewall (WAF) detects a request missing proper session cookies or browser fingerprints.
  - **Amazon:** Returned `200 OK` but gave an empty `jobs: []` array. This is a classic "shadowban" response where the server pretends the request worked but gives no data because there is no valid human session.

## 5. Network Traffic Interception (Playwright Sniffing)

- **Approach:** Wrote a sophisticated script that opened the browser, let it act like a normal user to pass browser fingerprinting, and silently "sniffed" the network traffic (`page.on('response')`) to intercept the raw JSON data the page requested for itself.
- **Result:** **Failed (Advanced Bot Detection).**
- **Analysis:** Even though the Amazon API response was captured, it still returned `0` jobs. Akamai/AWS WAF detected that the Chromium instance was running in `headless=True` mode (headless browsers expose certain fingerprint flags, e.g., missing plugins, specific WebGL signatures) and quietly dropped the payload.

---

## Conclusion & Recommendations

If the primary goal is **absolute safety from bans**:

1.  **Google is a goldmine.** They don't hide their jobs behind SPAs or anti-bot walls. Basic HTML scraping works flawlessly.
2.  **"Keyboard-only" via headless automation is conceptually safe but practically broken** on enterprise career sites due to cookie modals, shadow DOMs, and custom JS event listeners that ignore native `Enter` keys.
3.  **Headless browsers are heavily fingerprinted.** The moment a headless browser connects to `amazon.jobs`, they know it is a bot and serve empty data.

**Future Architecture Recommendation:**
Rather than fighting custom career portals, the most robust approach is to either:

---

1.  **Use a job-board aggregator API** (like scraping Wellfound/Cutshort).
2.  **Use Search Engine APIs** (Google Custom Search targeting `site:careers.microsoft.com`).
3.  **Run with full headful browsers natively** using stealth plugins if direct portal scraping is an absolute requirement.

---

## 6. The Production Winner: Manual Stealth Mode (Default)

### Why this approach?

We chose this because it is **100% ban-proof.** Modern anti-bot systems (Akamai, Cloudflare, AWS WAF) are designed to detect _patterns_ of headless automation. By using a **Headful Passive Listener**, we leverage your real, human navigation. You drive the browser; the script silently captures the results.

### The User Journey

1.  **Launch:** You run the script; it opens your actual Chrome profile in a visible window.
2.  **Hand-off:** You navigate to the target site and perform the initial search/login.
3.  **Activation:** Once on the results page, you signal the script to start.
4.  **Assisted Navigation:** The script scrolls or clicks "Next," while silently "sniffing" the background JSON traffic.
5.  **Data Persistence:** Every raw JSON payload is saved instantly to a local directory, bypassing the need for fragile DOM selectors.

### Generalization: How to adapt for ANY Career Portal

To target a new company (e.g., Apple, Netflix, NVIDIA):

1.  **Identify the API:** Open DevTools > Network tab. Filter by `Fetch/XHR`. Refresh the jobs page and look for the response containing the job list.
2.  **Update Keywords:** In the `handle_response` function, add the company's specific API URL fragments (e.g., `api/v1/jobs`) to the filter list.
3.  **Selector Mapping:** If the site uses infinite scroll, the generic `scroll` command works. If it uses a button, update the `page.click()` target to the "Next" button's CSS selector.
4.  **Profile Path:** Ensure the `USER_DATA_DIR` points to your primary browser's data folder to inherit your existing trust score.

### Strict Best Practices

1.  **NEVER go Headless:** The moment `headless=True` is detected, your IP trust score drops. Stay headful.
2.  **Use Persistent Context:** Always launch with your real user profile. Cookies are your shield.
3.  **Rate Limit by Heartbeat:** Don't click "Next" as fast as possible. Use `asyncio.sleep()` with random jitter (3-7 seconds) to mimic human reading time.
4.  **Sniff, Don't Scrape:** Prioritize `page.on('response')` over `page.query_selector()`. API data is structured and doesn't break when they redesign the website.
5.  **The "Beep" Alert:** Implement a sound notification if the script encounters a 403 or a CAPTCHA so you can intervene immediately.

### [Microsoft] Learning Case (2026-03-04 06:42:15)

- **Error**: Lazy loading blocks card extraction
- **Solution**: Implement pre-scroll using scrollTo(0, scrollHeight) before wait_for_selector

### [Amazon] Learning Case (2026-03-04 06:50:30)

- **Error**: Manual capture initially ignored Amazon due to strict URL keyword filtering.
- **Solution**: Broadened filters (`v1`, `v2`, `api`) and added a visual `[JSON]` log in the terminal to help the user identify capture-worthy traffic.
- **Error**: Export failed because Amazon returns a _list_ of jobs in one JSON, while the parser expected a single object.
- **Solution**: Implemented a **Normalization Layer** in `universal_export` that detects both detail objects and search result lists, making the script truly platform-agnostic.

### [System-Wide] Automated Learning Loop (2026-03-04 07:11:00)

Both the **Manual Stealth Mode** and **Automated Mode [BETA]** now feature an integrated **Learning Loop**.

- **Mechanism**: All catchable exceptions (JSON schema shifts, selector timeouts, network drops) trigger the `log_learning` function.
- **Persistence**: Errors and inferred solutions are automatically appended to this document to prevent repeating the same mistakes in future sessions.
- **Unified Schema**: Both engines now export a consistent CSV structure (`Job Title`, `Job ID`, `Location`, `Description`, `Apply Link`) to ensure seamless downstream JD processing.

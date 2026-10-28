# 🧪 PhishGuard Testing, Assumptions & Technical Boundaries

> **Academic Course:** Database Management Systems (Course Code: 102040305)  
> **Institution:** CVM University (ADIT) · Semester 3 B.Tech  
> **Document Purpose:** Complete audit trail of project assumptions, verified test cases, and operational limitations.

---

## 1. Project Assumptions

1. **Local MySQL Availability:**
   - The application assumes a MySQL 8.0+ server is running locally on port 3306 (or configured host/port) with the `phishguard_db` database created and initialized via `database/schema.sql` and `database/seed_rules.sql`.
   - Database credentials are assumed to be supplied via environment variables (`DB_PASSWORD`, `DB_USER`, `DB_HOST`, `DB_PORT`, `DB_NAME`).

2. **Offline Fallback Store:**
   - If MySQL is offline, unreachable, or credentials are unset, the system assumes the local filesystem has write access to `data/scan_history.json` to preserve scan records as an offline backup.

3. **URL Protocol Scope:**
   - The system assumes valid web URLs use standard `http://` or `https://` schemes. Non-web protocols (`ftp://`, `ssh://`, `mailto:`, `file:///`) are assumed to be out-of-scope and rejected by `utils/validators.py`.

4. **Rule Weights Synchronization:**
   - `config.py` in Python is the single source of truth for runtime heuristic weights. The `rules` table in MySQL stores base weights for reporting and audit history.

---

## 2. Verified Test Cases (Passed & Confirmed)

| Test Category | Test Case Description | Expected Result | Status |
|---|---|---|:---:|
| **Input Validation** | Empty string submitted to `validate_url("")` | Raises custom `InvalidURLError("A URL must be entered.")` | ✅ PASS |
| **Input Validation** | Missing scheme submitted (`"example.com"`) | Raises `InvalidURLError("The URL must start with http:// or https://")` | ✅ PASS |
| **Input Validation** | Malformed protocol (`"ftp://files.example.com"`) | Raises `InvalidURLError("Unsupported scheme: ftp")` | ✅ PASS |
| **Input Validation** | Whitespace padding (`"   https://example.com   "`) | Automatically trimmed and normalized to `"https://example.com"` | ✅ PASS |
| **Lexical Extraction** | URL parsing on `"https://user@sub.example.co.uk:8080/path?q=1#frag"` | Correctly extracts scheme, subdomain, registered domain, port, path, query, fragment | ✅ PASS |
| **Heuristic Evaluation** | Raw IP hostname (`"http://198.51.100.7/login"`) | Triggers `ip_address` (+25) and `https_check` (+10) rules | ✅ PASS |
| **Heuristic Evaluation** | Punycode homograph (`"https://xn--pple-43d.com/signin"`) | Triggers `punycode` (+20) and keyword rules | ✅ PASS |
| **Heuristic Evaluation** | Long URL threshold testing (>75 chars vs >100 chars) | Correctly awards +10 for long URLs and +15 for very long URLs | ✅ PASS |
| **Score Classification** | Score 20 vs 45 vs 75 | Correctly classifies as `Low Risk`, `Suspicious`, and `High Suspicion` | ✅ PASS |
| **MySQL Connection** | Missing `DB_PASSWORD` environment variable | Raises clean `RuntimeError` without crashing UI or leaking credentials | ✅ PASS |
| **Atomic Transaction** | `ScanRepository.save_scan(result)` on valid `URLResult` | Header inserted in `scans`, 16 rows inserted in `scan_rules`, committed atomically | ✅ PASS |
| **CHECK Constraints** | Attempt insert with `risk_score = 150` | MySQL rejects insert with CHECK constraint violation error | ✅ PASS |
| **Cascading Deletes** | `ScanRepository.delete_scan(scan_id)` executed | Row deleted from `scans`; all child rows in `scan_rules` auto-purged (`ON DELETE CASCADE`) | ✅ PASS |
| **Transaction Rollback** | Simulated failure in `database/transactions.sql` | `ROLLBACK` executes; zero orphaned or partial rows persist | ✅ PASS |
| **Database Views** | Querying `SELECT * FROM scan_summary` | Pre-computed summary returned with URL preview and count of triggered checks | ✅ PASS |
| **Analytical Queries** | Executing all 6 queries in `database/queries.sql` | Sub-millisecond execution with accurate group-by and window aggregations | ✅ PASS |
| **Web UI Integration** | Launching `streamlit run app.py` | UI renders cleanly; live DB badge displays status; dual-tab history active | ✅ PASS |
| **CLI Persistence** | Executing `python cli.py "<url>"` | Console report prints and record is auto-persisted to MySQL with `scan_id` | ✅ PASS |

---

## 3. Operational Limitations & Known Boundaries

1. **Heuristic False Positives:**
   - Legitimate banking or corporate portals often contain security keywords (e.g. `https://login.microsoftonline.com/common/oauth2`). While structural weights mitigate false alarms, keywords alone can cause slight score inflation.

2. **Heuristic False Negatives:**
   - Sophisticated phishing operations that register fresh domains and use short, clean-looking URLs (e.g. `https://clean-domain.xyz/auth`) may exhibit few lexical signals and receive a `Low Risk` score.

3. **Static vs. Dynamic Analysis:**
   - PhishGuard evaluates URLs strictly as text strings. It cannot inspect rendered DOM content, execute JavaScript, detect obfuscated iframes, or observe server-side HTTP redirects without visiting the target server.

4. **Local Dictionary Limitations:**
   - The keyword dictionaries, suspicious TLD lists, and URL shortener catalogs in `data/` are static reference lists. They provide substantial coverage for demonstration but cannot be fully comprehensive across the entire global internet.

5. **Decoupled Live SSL Checking:**
   - `utils/ssl_checker.py` establishes a live TCP socket connection to retrieve SSL certificate metadata. Because PhishGuard’s core engine is strictly static, this live checker is maintained as a separate, optional utility module.

---

## 4. Future Enhancements & Scope

1. **Threat Intelligence Feed Ingestion:**
   - Scheduled background tasks to pull open-source phishing feeds (e.g., PhishTank, OpenPhish) into a MySQL `threat_signatures` table for instant $O(1)$ blacklist matching.

2. **Machine Learning Hybrid Pipeline:**
   - Train a supervised classification model (such as Random Forest or XGBoost) on the 25+ lexical features extracted by `core/feature_extractor.py` to complement heuristic weights with probabilistic predictions.

3. **Enterprise Role-Based Access Control (RBAC):**
   - Store hashed user credentials and role permissions (Administrator, Security Analyst, Auditor) in MySQL with comprehensive audit trails for organizational compliance.

4. **Automated PDF Export & Webhook Alerts:**
   - Implement scheduled compliance report generation and automated alerts (via email or Slack webhooks) whenever a `High Suspicion` URL is scanned.

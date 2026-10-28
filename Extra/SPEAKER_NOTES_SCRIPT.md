# 🎙️ PhishGuard Presentation Script & Speaker Notes

> **Audience:** College Faculty & External Examiners  
> **Course:** Database Management Systems (Course Code: 102040305)  
> **Programme:** B.Tech Semester 3 — CVM University (ADIT)  
> **Total Target Duration:** 7 – 10 Minutes (approx. 40–50 seconds per slide)

---

## ⏱️ Presentation Timing Plan

| Slide # | Slide Title | Target Time | Cumulative |
|:---:|:---|:---:|:---:|
| **Slide 1** | Title Slide & Academic Identity | 0:40 | 0:40 |
| **Slide 2** | Problem Statement & Research Motivation | 0:45 | 1:25 |
| **Slide 3** | Project Objectives & Architectural Scope | 0:45 | 2:10 |
| **Slide 4** | System Architecture & Data Flow Pipeline | 0:50 | 3:00 |
| **Slide 5** | Python Implementation & Modular Architecture | 0:45 | 3:45 |
| **Slide 6** | MySQL Database Design & ER Modeling | 0:50 | 4:35 |
| **Slide 7** | Core DBMS Concepts & Normalization Defense | 0:50 | 5:25 |
| **Slide 8** | Real SQL Query Demonstrations | 0:50 | 6:15 |
| **Slide 9** | Interface Demonstration (Streamlit Web & CLI) | 0:45 | 7:00 |
| **Slide 10** | Testing Verification & System Limitations | 0:45 | 7:45 |
| **Slide 11** | Future Scope & Production Roadmap | 0:40 | 8:25 |
| **Slide 12** | Conclusion & Key Viva Q&A | 0:50 | 9:15 |

---

## 📋 Slide-by-Slide Speaking Script

### Slide 1: Title Slide & Academic Identity (0:00 – 0:40)
> **What to Say:**  
> "Respected faculty members, project guide, and examiners, good morning.  
> Today, I am pleased to present our Semester 3 B.Tech mini-project: **PhishGuard — Rule-Based Static URL Security Analysis System with MySQL Relational Database Integration**.  
> This project was developed for our **Database Management Systems** course (Course Code: 102040305) at CVM University.  
> PhishGuard bridges cybersecurity and database engineering: it inspects suspicious web links purely through static lexical analysis without visiting the target server, and persists complete scan outcomes into an enterprise-grade MySQL relational database.  
> Over the next eight minutes, I will walk you through the security analysis pipeline, our normalized 3NF database schema, multi-table SQL queries, and ACID-compliant transaction handling."

---

### Slide 2: Problem Statement & Research Motivation (0:40 – 1:25)
> **What to Say:**  
> "To understand the motivation behind PhishGuard, we must look at the current threat landscape.  
> Phishing remains the single most common digital attack vector, responsible for over 80% of reported credential thefts and online financial fraud. Attackers craft fraudulent URLs that imitate trusted banking institutions, university portals, and cloud providers.  
> However, traditional security tools often employ **dynamic analysis** — meaning they actually connect to the website or follow redirects. This presents serious risks: it exposes the client machine to drive-by malware payloads, lets attackers log the client's IP address, and allows evasion kits to serve fake benign pages when they detect an automated crawler.  
> PhishGuard solves this problem by using **static analysis**. We treat the URL strictly as text. Malicious URLs almost always exhibit structural red flags — such as raw IP addresses, '@' symbol trickery, excessive subdomains, or look-alike punycode characters.  
> Furthermore, typical standalone security scripts lack persistence; once the terminal closes, the scan data vanishes. Integrating MySQL transforms static scoring into an auditable, queryable security database."

---

### Slide 3: Project Objectives & Architectural Scope (1:25 – 2:10)
> **What to Say:**  
> "Our project objectives are divided into two complementary domains:  
> On the **Python side**, we set out to build a pure Python analysis pipeline: validating URLs without crashes, extracting 25+ lexical and structural metrics, evaluating 16 weighted heuristic inspection rules, and mapping the cumulative score to an objective risk level — Low Risk, Suspicious, or High Suspicion.  
> On the **Database side**, our objective was to design a clean 3NF relational schema in MySQL, enforce entity and referential integrity through composite primary keys and cascading constraints, execute atomic transactions, and enable analytical reporting through views and multi-table queries.  
> Just as importantly, we define our **architectural boundaries**:  
> First, our static guarantee: target URLs are never opened, fetched, or executed.  
> Second, we emphasize that our system provides a heuristic risk signal rather than an absolute antivirus verdict.  
> Third, our presentation layer contains zero SQL — all database operations are cleanly encapsulated in an isolated service repository."

---

### Slide 4: System Architecture & Data Flow Pipeline (2:10 – 3:00)
> **What to Say:**  
> "Here we see the end-to-end architecture of PhishGuard.  
> The workflow begins when a user submits a URL via either the Streamlit web dashboard or the command-line interface.  
> The URL enters `utils/validators.py` for syntax normalization and XSS sanitization. Next, `core/url_parser.py` decomposes the link into its structural parts — scheme, hostname, registered domain, path, query, and fragment.  
> The `FeatureExtractor` measures 25+ metrics, and `RuleEngine` evaluates 16 weighted heuristic checks. Each rule outputs a strongly typed `RuleResult` object. The `RiskCalculator` sums these points (capped at 100) and assigns the risk level.  
> Now comes the persistence layer: the complete `URLResult` is handed to `ScanRepository`.  
> `ScanRepository` opens a MySQL connection, initiates a transaction, inserts the scan header into `scans`, dynamically resolves rule IDs, inserts all 16 evaluated rule rows into `scan_rules`, and issues a `COMMIT`. If MySQL happens to be offline, the system catches the error gracefully and alerts the user while preserving the scan in a local JSON fallback file."

---

### Slide 5: Python Implementation & Modular Architecture (3:00 – 3:45)
> **What to Say:**  
> "Looking at the Python codebase, we adhered strictly to modular software engineering and object-oriented principles.  
> The codebase maps directly to our Python syllabus:  
> In **Unit 5 (Data Structures)**, we utilized Tuples for immutable protocol schemes, Sets for O(1) membership lookups of special characters and URL shorteners, Dictionaries for weighted rule tables, and Lists for collecting flagged indicators.  
> In **Unit 6 (Classes & Exceptions)**, we encapsulated analysis logic inside `URLAnalyzer` and domain entities inside `URLResult`, `RuleResult`, and `ScanRecord`. We created a custom exception, `InvalidURLError`, ensuring malformed URLs are caught cleanly without crashing the program.  
> As shown in the code snippet on the right, the entire analysis lifecycle is clean, readable, and ends with a single call to `ScanRepository.save_scan(result)`."

---

### Slide 6: MySQL Database Design & ER Modeling (3:45 – 4:35)
> **What to Say:**  
> "Turning to our database implementation, we designed a normalized relational schema consisting of three tables:  
> 1. Table `scans`: stores the scan header — `scan_id` as an auto-incrementing primary key, the URL string, the integer risk score with a `CHECK` constraint (0–100), the risk level, and an automatic timestamp. It is indexed on `scanned_at` in descending order.  
> 2. Table `rules`: acts as our master catalog containing 18 seeded heuristic definitions with a unique `rule_code` and base weight.  
> 3. Table `scan_rules`: is our junction table modeling the Many-to-Many relationship between scans and rules.  
> I want to draw your attention to our key design choices:  
> We implemented a **Composite Primary Key** on `(scan_id, rule_id)`. This naturally guarantees that each rule is evaluated at most once per scan without wasting storage on an artificial surrogate key.  
> Furthermore, we configured `ON DELETE CASCADE` on `scan_id`. If a user deletes a scan record, MySQL automatically removes all child rows in `scan_rules`, completely eliminating the risk of orphaned data. Conversely, on `rule_id`, we set `ON DELETE RESTRICT` to protect our master rule definitions."

---

### Slide 7: Core DBMS Concepts & Normalization Defense (4:35 – 5:25)
> **What to Say:**  
> "Slide 7 summarizes how PhishGuard demonstrates key syllabus concepts:  
> First, **Normalization**:  
> In **1NF**, all column values are atomic. Rather than storing comma-separated rule lists, each rule check is a distinct row in `scan_rules`.  
> In **2NF**, non-key attributes in `scan_rules` (`triggered`, `points_awarded`) functionally depend on the *entire* composite key `(scan_id, rule_id)`, not just part of it.  
> In **3NF and BCNF**, rule metadata (`rule_name`, `weight`) depends solely on the candidate key `rule_id`. There are zero transitive dependencies.  
> Second, **Integrity Constraints**: We enforce domain constraints via two `CHECK` constraints on score range and categorical risk levels, plus a `UNIQUE` constraint on `rule_code`.  
> Third, **Views & Indexes**: We created the `scan_summary` view to provide a pre-compiled, aggregated summary of scans without exposing raw table complexity.  
> Fourth, **Transactions**: All writes in `ScanRepository` are wrapped in `START TRANSACTION`, `COMMIT`, and `ROLLBACK`, guaranteeing atomicity."

---

### Slide 8: Real SQL Query Demonstrations (5:25 – 6:15)
> **What to Say:**  
> "On this slide, we showcase four real SQL queries from our `database/queries.sql` file:  
> - **Query 1** demonstrates basic DML retrieval: projection, string manipulation using `LEFT()` to format long URLs into 50-character previews, and indexed descending sorting.  
> - **Query 2** calculates our threat distribution using `GROUP BY risk_level` combined with an advanced SQL window function: `ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)`. This computes exact categorical percentages in a single query.  
> - **Query 3** is our multi-table relational inner `JOIN`. It joins `scans` to `scan_rules` and then to `rules` where `triggered = TRUE`, providing a full drill-down of which heuristics fired for each URL.  
> - **Query 4** provides temporal analytics using `YEAR()` and `MONTH()`, computing average risk scores and utilizing conditional aggregation with `SUM(risk_level = 'High Suspicion')` to count critical threats per month.  
> Every query uses parameterized inputs to guarantee complete protection against SQL injection."

---

### Slide 9: Interface Demonstration & Results (6:15 – 7:00)
> **What to Say:**  
> "PhishGuard provides two user interfaces:  
> Our primary interface is the **Streamlit web application**. On the Scanner page, users can submit URLs or click pre-configured synthetic samples to test raw IP hostnames, punycode strings, or long links. The scan result displays an animated risk score meter, a color-coded risk badge, and an expandable indicator drill-down.  
> On the **History page**, we built a dual-tab architecture:  
> The 'MySQL Database History' tab pulls live relational records, supporting search, risk-level filtering, inspection of joined rule checks, and interactive row deletion to verify cascading deletes.  
> The 'JSON Backup History' tab provides local fallback.  
> On the **Dashboard page**, real-time metric cards and distribution bars are populated directly by our SQL aggregation queries.  
> In the sidebar, a live connection indicator actively probes MySQL, displaying green when online and red when offline.  
> In addition, our **CLI interface (`cli.py`)** allows rapid terminal testing and automatically persists scan records to MySQL."

---

### Slide 10: Testing Verification & Limitations (7:00 – 7:45)
> **What to Say:**  
> "In academic engineering, honest testing and acknowledging limitations are paramount.  
> On the left, we highlight our verified test cases:  
> We verified URL validation against malformed protocols (`ftp://`) and illegal hostnames. We tested all 16 heuristic rules, confirmed atomic insertion of header and junction rows, validated that `CHECK` constraints reject illegal scores, demonstrated that `ON DELETE CASCADE` purges child records, and verified `ROLLBACK` in `transactions.sql`.  
> On the right, we openly address our limitations:  
> Heuristic analysis can yield **false positives** on legitimate corporate URLs containing login keywords, and **false negatives** on brand-new domains with short paths. Because we are strictly static, we cannot inspect runtime JavaScript or follow server-side HTTP redirects. We also note that while we implemented an SSL checker module, live socket checks require network connectivity and are therefore decoupled from the static pipeline."

---

### Slide 11: Future Scope & Production Roadmap (7:45 – 8:25)
> **What to Say:**  
> "Looking toward the future, PhishGuard provides a strong architectural foundation for four production enhancements:  
> 1. **Threat Intelligence Ingestion**: Implementing automated cron jobs to pull open-source phishing feeds like PhishTank directly into MySQL tables for O(1) blacklist lookups.  
> 2. **Machine Learning Hybrid Scoring**: Using our 25+ extracted features to train a Random Forest classifier, fusing empirical static weights with probabilistic machine learning predictions.  
> 3. **Role-Based Access Control (RBAC)**: Storing user credentials and roles (Admin, Security Analyst, Auditor) in MySQL with comprehensive audit trails.  
> 4. **Automated Reporting**: Generating downloadable executive PDF audit summaries and dispatching webhook alerts to security teams upon detecting high-suspicion URLs."

---

### Slide 12: Conclusion & Key Viva Q&A (8:25 – 9:15)
> **What to Say:**  
> "To conclude: PhishGuard proves that static lexical analysis provides a safe, zero-risk method for detecting phishing threats, while MySQL delivers the normalization, data integrity, and analytical power required for security monitoring.  
> To conclude our presentation, we address three fundamental viva questions:  
> 1. *Why MySQL over a JSON file?* JSON files must be loaded entirely into RAM to search, risk corruption during concurrent writes, and cannot enforce constraints. MySQL provides indexed lookups, BCNF normalization, ACID transactions, and declarative SQL aggregations.  
> 2. *Why a composite primary key on `scan_rules`?* `(scan_id, rule_id)` naturally prevents duplicate evaluations of the same rule in a single scan without wasting storage on an artificial surrogate key.  
> 3. *How do transactions and CASCADE constraints prevent anomalies?* `START TRANSACTION` with `COMMIT` and `ROLLBACK` guarantees atomicity across parent and child tables, while `ON DELETE CASCADE` eliminates orphaned records upon deletion.  
> Thank you for your time and guidance. I welcome your questions."

---

## 🎯 Tips for the Live Demonstration

1. **If MySQL is Running:**
   - Open PowerShell, set `$env:DB_PASSWORD = "your_password"`, and run `streamlit run app.py`.
   - Point out the **🟢 MySQL Online** badge in the sidebar.
   - Run a scan with a sample URL (e.g. `http://198.51.100.7/secure-bank/login.php`).
   - Switch to the **🗂️ Scan History** tab -> **🗄️ MySQL Database History** tab. Show the new row with its generated `scan_id`.
   - Click on the scan dropdown to show the joined rule breakdown (`scans ⋈ scan_rules ⋈ rules`).
   - Click **🗑️ Delete this scan from MySQL** to prove `ON DELETE CASCADE`.

2. **If Asked to Show SQL in Terminal:**
   - Run: `mysql -u root -p phishguard_db < database/queries.sql`
   - Point out Query 2 (risk percentages) and Query 3 (3-table join).

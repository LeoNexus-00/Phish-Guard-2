# PhishGuard 🛡️ — Static URL Security Analysis with MySQL DBMS Integration

> **Educational Rule-Based Static URL Security Analysis & DBMS Integration System**  
> *Semester 3 B.Tech Mini-Project — Database Management Systems (DBMS) & Python Programming*

---

## 📌 Project Overview

**PhishGuard** is a security-focused URL analysis platform developed to inspect and score Uniform Resource Locators (URLs) for signs of phishing and malicious engineering **without visiting or fetching the destination web server**.

This enhanced version integrates an enterprise-grade **MySQL relational database** alongside the existing Python rule engine and Streamlit web dashboard. The project showcases complete **Database Management System (DBMS)** principles: relational schema design, 3NF normalization, referential integrity with cascading constraints, composite primary keys, multi-table JOINs, aggregate reporting, database views, and ACID-compliant transaction handling (COMMIT / ROLLBACK).

---

## 🏛️ Relational Database Architecture

The persistence model consists of 3 normalized relational tables designed to eliminate redundancy while preserving historical audit accuracy.

### Entity-Relationship (ER) Diagram

```text
┌───────────────────────────────────────┐         ┌───────────────────────────────────────┐
│                 scans                 │         │                 rules                 │
├───────────────────────────────────────┤         ├───────────────────────────────────────┤
│ PK  scan_id     INT AUTO_INCREMENT    │         │ PK  rule_id    INT AUTO_INCREMENT     │
│     url         VARCHAR(2048) NOT NULL│         │ UQ  rule_code  VARCHAR(50) NOT NULL   │
│     risk_score  INT NOT NULL          │         │     rule_name  VARCHAR(100) NOT NULL  │
│     risk_level  VARCHAR(20) NOT NULL  │         │     weight     INT NOT NULL           │
│     scanned_at  TIMESTAMP DEFAULT NOW │         └───────────────────┬───────────────────┘
└───────────────────┬───────────────────┘                             │
                    │ 1                                               │ 1
                    │                                                 │
                    │         ┌───────────────────────────────────────┤
                    ▼         ▼                                       │
         ┌──────────────────────────────────────────────────┐         │
         │                    scan_rules                    │         │
         ├──────────────────────────────────────────────────┤         │
         │ PK, FK1  scan_id        INT (FK → scans.scan_id) │         │
         │ PK, FK2  rule_id        INT (FK → rules.rule_id) │         │
         │          triggered      BOOLEAN NOT NULL         │         │
         │          points_awarded INT DEFAULT 0            │         │
         └──────────────────────────────────────────────────┘         │
                                                                      │
Cardinality & Rules:                                                  │
  • scans     1 ──< scan_rules (one scan records outcomes for many rules)
  • rules     1 ──< scan_rules (one rule is evaluated across many scans)
  • Composite PK (scan_id, rule_id) prevents duplicate checks per scan
  • ON DELETE CASCADE on scans: Deleting a scan automatically purges its rule results
  • ON DELETE RESTRICT on rules: Prevents accidental deletion of rule definitions
```

### Normalization Rationale (1NF → BCNF)
- **1NF (First Normal Form):** All column attributes are atomic. Repeating indicators and comma-separated lists have been eliminated from `scans` and modeled as individual rows in `scan_rules`.
- **2NF (Second Normal Form):** Every non-key column in `scan_rules` (`triggered`, `points_awarded`) depends on the **entire composite primary key** `(scan_id, rule_id)`, not just part of it.
- **3NF & BCNF:** In `rules`, non-key attributes (`rule_name`, `weight`) depend solely on the candidate key `rule_id` / `rule_code`. No transitive dependencies exist.

---

## 🎓 DBMS Concepts Demonstrated (Faculty Checklist)

| Concept | Implementation in PhishGuard |
|---|---|
| **Relational Schema Design** | 3 normalized tables: `scans`, `rules`, and junction table `scan_rules` |
| **Primary Keys (PK)** | `scans.scan_id` (AUTO_INCREMENT), `rules.rule_id` (AUTO_INCREMENT) |
| **Composite Primary Key** | `scan_rules(scan_id, rule_id)` guarantees uniqueness of rule evaluations per scan |
| **Foreign Keys & Referential Integrity** | `scan_rules.scan_id → scans` (`ON DELETE CASCADE`), `scan_rules.rule_id → rules` (`ON DELETE RESTRICT`) |
| **CHECK Constraints** | `chk_score` (`risk_score BETWEEN 0 AND 100`), `chk_risk_level` (`IN ('Low Risk', 'Suspicious', 'High Suspicion')`) |
| **UNIQUE Constraints** | `rules.rule_code UNIQUE` |
| **Indexing** | B-Tree index on `scans(scanned_at DESC)` for fast history queries |
| **Database Views** | `scan_summary` view aggregating scan metrics with `LEFT JOIN` and column aliasing |
| **Multi-Table JOINs** | 3-table join (`scans` ⋈ `scan_rules` ⋈ `rules`) to inspect scan heuristic breakdown |
| **SQL Aggregations & Grouping** | `COUNT(*)`, `AVG(risk_score)`, `GROUP BY risk_level`, `GROUP BY YEAR, MONTH` |
| **Window Functions** | `ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)` for risk distribution % |
| **ACID Transactions (Atomicity)** | Single transaction commits both scan header and all 16 check results; rollback on error |
| **Database Security** | Zero hardcoded credentials; connection via environment variables; 100% parameterized queries (`%s`) preventing SQL injection |
| **Python-DB Integration** | Clean Repository pattern in `services/scan_repository.py` isolating all SQL logic |

---

## 📁 Project Structure

```text
DBMS/
│
├── app.py                         # Streamlit Web UI (Scanner, History, Dashboard, About)
├── cli.py                         # Command-line interface with automatic MySQL persistence
├── config.py                      # Central configuration (weights, thresholds, risk levels)
├── requirements.txt               # Dependencies (streamlit, pandas, mysql-connector-python)
├── README.md                      # Complete project & DBMS documentation
│
├── database/                      # Database DDL, Seed, Queries & Transactions
│   ├── __init__.py                # Package initializer
│   ├── connection.py              # Secure MySQL connection factory (reads env vars)
│   ├── schema.sql                 # DDL: CREATE TABLE, PK, FK, CHECK, INDEX, VIEW
│   ├── seed_rules.sql             # DML: INSERT 18 security heuristic rules
│   ├── queries.sql                # 6 demonstration SQL queries (Joins, Aggregates, Views)
│   └── transactions.sql           # ACID transaction demonstration (COMMIT vs ROLLBACK)
│
├── services/                      # Business & Data Access Services
│   ├── scan_repository.py         # Repository pattern: all SQL queries & DB operations
│   ├── history_manager.py         # Secondary JSON storage (offline fallback)
│   └── statistics.py              # Aggregation utilities
│
├── core/                          # Heuristic Analysis Engine
│   ├── analyzer.py                # Pipeline controller
│   ├── feature_extractor.py       # Extracts 25+ lexical and structural features
│   ├── risk_calculator.py         # Weighted scoring & risk level categorization
│   ├── rule_engine.py             # Heuristic rules evaluation
│   └── url_parser.py              # URL decomposition
│
├── models/                        # Object-Oriented Domain Models
│   ├── scan_record.py             # ScanRecord entity
│   └── url_result.py              # URLResult and RuleResult entities
│
├── utils/                         # Helper Utilities
│   ├── helpers.py                 # String formatters and report generators
│   └── validators.py              # URL syntax validation & custom InvalidURLError
│
└── data/                          # Reference Dictionaries & Fallback JSON Store
    ├── scan_history.json          # Offline JSON backup
    ├── suspicious_keywords.json
    ├── suspicious_tlds.json
    └── url_shorteners.json
```

---

## ⚙️ Setup & Installation

### 1. Environment Preparation (Windows PowerShell)

Set the MySQL database connection credentials in your PowerShell terminal:

```powershell
$env:DB_HOST     = "localhost"
$env:DB_PORT     = "3306"
$env:DB_USER     = "root"
$env:DB_PASSWORD = "your_mysql_password_here"
$env:DB_NAME     = "phishguard_db"
```

> **Note:** If `DB_PASSWORD` is not set, PhishGuard gracefully operates in **Offline / JSON Backup mode** and alerts the user on the dashboard without crashing.

### 2. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Initialize MySQL Database & Schema

Run the DDL schema file to create `phishguard_db`, the three tables, indexes, and the summary view:

```powershell
mysql -u root -p < database/schema.sql
```

### 4. Seed the Rules Table

Populate the `rules` table with the 18 heuristic rule definitions:

```powershell
mysql -u root -p phishguard_db < database/seed_rules.sql
```

---

## 🚀 Running PhishGuard

### A. Streamlit Web Dashboard
Launch the graphical browser interface:
```powershell
streamlit run app.py
```
- **Scanner:** Submit any URL to run live heuristic checks. Results are automatically saved to MySQL (primary) and JSON (backup).
- **Scan History:** Dual-tab interface allowing inspection of MySQL relational records (with live join breakdown) or JSON fallback files. Includes single-scan deletion (demonstrating `ON DELETE CASCADE`) and full clearing.
- **Dashboard:** Dual-tab analytics presenting SQL aggregations (`GROUP BY`, `AVG`, `COUNT`) and top-triggered rules via multi-table JOINs.
- **Sidebar:** Live MySQL connection status badge (🟢 Connected / 🔴 Offline).

### B. Command-Line Interface (CLI)
Run quick scans directly in your terminal:
```powershell
# Interactive mode
python cli.py

# Single URL scan
python cli.py "http://198.51.100.7/secure-login/verify.php"
```
The CLI automatically prints the analysis report and saves the record to MySQL.

---

## 🔍 Demonstration Queries (`database/queries.sql`)

You can execute the demonstration queries against your MySQL database:

```powershell
mysql -u root -p phishguard_db < database/queries.sql
```

### Summary of Included Queries:
1. **Query 1 (Scan History):** `SELECT ... ORDER BY scanned_at DESC`
2. **Query 2 (Risk Distribution):** `GROUP BY risk_level` with percentage calculation using `SUM(COUNT(*)) OVER ()`
3. **Query 3 (Triggered Rules per Scan):** 3-table join (`scans ⋈ scan_rules ⋈ rules`) filtering on `triggered = TRUE`
4. **Query 4 (Most Frequently Triggered Indicators):** Top-N query with `GROUP BY r.rule_id`, `COUNT(*)`, and `LIMIT 10`
5. **Query 5 (Monthly Trend Analytics):** Time-series aggregation using `YEAR(scanned_at)`, `MONTH(scanned_at)`, and conditional `SUM()`
6. **Query 6 (Database View Utilization):** Querying the pre-compiled `scan_summary` view with custom filter criteria

---

## 💳 ACID Transactions Demonstration (`database/transactions.sql`)

Demonstrate transaction atomicity and rollback behavior directly in the MySQL shell:

```powershell
mysql -u root -p phishguard_db
```

Inside MySQL:
```sql
SOURCE database/transactions.sql;
```

- **Demo A (COMMIT):** Starts a transaction, inserts a scan header, retrieves `LAST_INSERT_ID()`, inserts corresponding `scan_rules` rows, and executes `COMMIT`. All changes persist.
- **Demo B (ROLLBACK):** Starts a transaction, inserts a test scan, encounters an intentional failure / issue, and executes `ROLLBACK`. Demonstrates that **no orphaned or partial data** is saved to the database.

---

## 🛡️ Heuristic Rules Evaluated

PhishGuard checks 16 weighted structural and lexical rules:

1. **HTTPS Check (+10)** — Absence of secure TLS protocol
2. **IP Address Hostname (+25)** — Raw IPv4/IPv6 used instead of domain name
3. **@ Symbol in Address (+20)** — Obfuscation syntax ignoring preceding prefix
4. **Suspicious Keywords (+10 per category)** — Presence of financial/credential lures (e.g. *login*, *verify*, *banking*)
5. **Keyword in Domain (+10)** — Brand impersonation in domain label
6. **URL Length (+10 / +15)** — Excessive URL length (>75 chars: +10, >100 chars: +15)
7. **Excessive Subdomains (+10)** — More than 3 subdomain levels
8. **Embedded Domain (+15)** — Domain name hidden inside subdomain hierarchy
9. **Hyphenated Hostname (+10)** — Excessive dashes used in spoofing
10. **Special Character Patterns (+10)** — Unusual symbols (`~`, `;`, `%`, `_`)
11. **URL Shortener (+10)** — Known masking services (bit.ly, tinyurl, etc.)
12. **Punycode / Homograph (+20)** — `xn--` prefix indicating non-ASCII internationalized look-alike characters
13. **URL Encoding (+10)** — Hex-encoded characters masking true target
14. **Suspicious TLD (+10)** — High-abuse top-level domains (.tk, .xyz, .top, etc.)
15. **Non-Standard Port (+10)** — Ports other than 80 or 443
16. **Hostname Digits (+5)** — Numeric strings embedded within hostname labels

---

## 👥 Viva & Academic Presentation Tips

- **Why a Composite PK on `scan_rules`?**  
  Each scan evaluates each rule exactly once. A composite key `(scan_id, rule_id)` prevents accidental duplicate evaluations for the same rule in a single scan while saving the need for an unnecessary surrogate auto-increment key.
- **Why use `ON DELETE CASCADE`?**  
  Scan results in `scan_rules` have no independent existence without their parent scan header in `scans`. When a scan is deleted, its detail rows are automatically cleaned up, preserving referential integrity with zero orphaned rows.
- **Why use `ON DELETE RESTRICT` on `rules`?**  
  Heuristic rules are master reference data. If a rule has been evaluated in historical scans, deleting the rule definition is restricted to avoid corrupting audit history.
- **How are SQL Injections prevented?**  
  All SQL queries in `ScanRepository` utilize parameterized placeholders (`%s`). User input is never concatenated or interpolated into SQL strings.
- **How is resilience achieved if MySQL is down?**  
  The system uses a graceful try/except wrapper around database interactions. If MySQL is offline, the application continues to function normally using its local JSON storage as a fallback.

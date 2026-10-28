# 🎓 PhishGuard Viva Preparation Cheatsheet

> **Course:** Database Management Systems (Course Code: 102040305)  
> **Programme:** B.Tech Semester 3 — CVM University (ADIT)  
> **Focus Areas:** Relational Modeling, 3NF Normalization, SQL Queries, ACID Transactions, and Python OOP Integration.

---

## 📌 Top 12 Expected Viva Questions & Model Answers

### Question 1: Why is a relational database (MySQL) better suited than a flat JSON file for this application?
**Model Answer:**  
"A flat JSON file has fundamental scalability, concurrency, and integrity limitations:
1. **Memory & I/O Overhead:** To search or sort a JSON file, the entire file must be read from disk and parsed into RAM. In contrast, MySQL uses B-Tree indexes to perform lookups in logarithmic time without loading unrelated records.
2. **Concurrency & Locking:** If multiple scans occur concurrently, a JSON file risks race conditions and data corruption because file writes are typically non-atomic. MySQL handles concurrent read/write transactions gracefully with row-level and table-level locking.
3. **Data Integrity:** A JSON file cannot enforce domain rules, data types, or foreign key constraints. MySQL strictly enforces primary keys, foreign keys, `CHECK` constraints, and data types at the storage engine level.
4. **Complex Analytics:** Computing metrics like threat distribution or top-triggered heuristics in JSON requires writing custom procedural loops. MySQL executes these declaratively in optimized C++ via SQL `GROUP BY`, `JOIN`, and aggregate functions."

---

### Question 2: Explain your database schema. Why did you use three tables instead of two or one?
**Model Answer:**  
"Our schema contains three tables: `scans`, `rules`, and `scan_rules`:
- **`scans`** records each URL analysis run (URL, risk score, risk level, timestamp).
- **`rules`** stores our master catalog of heuristic inspection rules and their assigned weights.
- **`scan_rules`** is the junction (or fact) table linking scans and rules.

If we used a **single flat table**, rule names and weights would be repeated for every scan record, violating 2NF and 3NF and causing update anomalies if a rule weight changed.  
If we used **two tables** (e.g., storing a comma-separated string of triggered rules in `scans`), we would violate 1NF because the attribute would not be atomic, making it impossible to index or query specific rules efficiently.  
The 3-table design correctly represents the **Many-to-Many relationship** between scans and heuristic rules."

---

### Question 3: How does your database design satisfy 1NF, 2NF, 3NF, and BCNF?
**Model Answer:**  
- **1NF (First Normal Form):** Every attribute contains atomic values (no repeating groups, no arrays, no comma-separated strings). Each rule check is recorded as its own row in `scan_rules`.
- **2NF (Second Normal Form):** All non-key attributes in `scan_rules` (`triggered`, `points_awarded`) functionally depend on the **entire composite primary key** `(scan_id, rule_id)`. There are no partial dependencies.
- **3NF (Third Normal Form):** There are no transitive dependencies. In `rules`, non-key attributes (`rule_name`, `weight`) depend solely on the candidate key `rule_id`. In `scans`, `risk_score` and `risk_level` describe the scan entity itself.
- **BCNF (Boyce-Codd Normal Form):** For every functional dependency $X \rightarrow Y$, the determinant $X$ is a superkey."

---

### Question 4: Why did you use a Composite Primary Key `(scan_id, rule_id)` on `scan_rules`?
**Model Answer:**  
"In a junction table representing an M:N relationship, a composite primary key formed by `(scan_id, rule_id)` is the most natural and efficient design:
1. **Uniqueness Guarantee:** It guarantees at the database level that a specific rule cannot be evaluated or inserted more than once for the same scan run.
2. **Eliminates Overhead:** It eliminates the need for an unnecessary surrogate auto-increment key (`id`), saving storage and index memory.
3. **Clustered Indexing:** In MySQL's InnoDB engine, tables are clustered by their primary key. Having `(scan_id, rule_id)` as the PK means all rule results for a particular scan are physically stored contiguously on disk, making scan detail queries extremely fast."

---

### Question 5: What is the purpose of `ON DELETE CASCADE` and `ON DELETE RESTRICT` in your schema?
**Model Answer:**  
"These define referential actions that maintain referential integrity:
- **`ON DELETE CASCADE` on `scan_rules.scan_id → scans.scan_id`:** A rule check result has no meaning without the parent scan. When a scan is deleted from `scans`, MySQL automatically removes all of its associated rows from `scan_rules`. This prevents orphaned rows.
- **`ON DELETE RESTRICT` on `scan_rules.rule_id → rules.rule_id`:** The `rules` table is a master reference catalog. If historical scans reference a rule, MySQL blocks any attempt to delete that rule definition, preventing corruption of historical audit trails."

---

### Question 6: What are CHECK constraints, and how are they implemented in your project?
**Model Answer:**  
"A `CHECK` constraint enforces domain integrity by specifying a boolean condition that every inserted or updated row must satisfy.  
In our `scans` table, we defined two `CHECK` constraints:
1. `CONSTRAINT chk_score CHECK (risk_score BETWEEN 0 AND 100)`: Guarantees that risk scores can never exceed valid boundaries or be negative.
2. `CONSTRAINT chk_risk_level CHECK (risk_level IN ('Low Risk', 'Suspicious', 'High Suspicion'))`: Enforces that only recognized risk category strings can be stored.  
If any INSERT or UPDATE violates these conditions, MySQL aborts the query with an error."

---

### Question 7: Explain the concept of ACID transactions and how they are demonstrated in your code.
**Model Answer:**  
"ACID guarantees reliable database transactions:
- **Atomicity:** 'All or nothing'. In `ScanRepository.save_scan()`, we wrap the header insert into `scans` and all 16 inserts into `scan_rules` inside a single transaction. If any insert fails, `connection.rollback()` is executed, leaving zero partial data.
- **Consistency:** The database transitions from one valid state to another, strictly obeying all PK, FK, and CHECK constraints.
- **Isolation:** Concurrent scans being saved simultaneously do not interfere with each other's uncommitted state.
- **Durability:** Once `connection.commit()` succeeds, the scan records are permanently saved to disk even in the event of a system crash.  
In `database/transactions.sql`, Demo A shows a successful commit, while Demo B demonstrates how rollback cleanly reverses changes when an error is encountered."

---

### Question 8: Explain Query 3: the 3-table JOIN. How does it work?
**Model Answer:**  
```sql
SELECT s.scan_id, r.rule_name, sr.points_awarded
FROM   scans s
JOIN   scan_rules sr ON s.scan_id  = sr.scan_id
JOIN   rules      r  ON sr.rule_id = r.rule_id
WHERE  sr.triggered = TRUE
ORDER  BY s.scan_id DESC;
```
"This query performs an **Inner Join** across three tables:
1. It joins the `scans` table `s` with the junction table `scan_rules` `sr` using the foreign key `s.scan_id = sr.scan_id`.
2. It then joins `sr` with the master `rules` table `r` using `sr.rule_id = r.rule_id`.
3. The `WHERE sr.triggered = TRUE` clause filters only those heuristic checks that detected suspicious patterns.
4. It projects the scan ID, human-readable rule name, and awarded points, ordered by newest scan first."

---

### Question 9: In Query 2, how does the window function `SUM(COUNT(*)) OVER ()` work?
**Model Answer:**  
```sql
SELECT risk_level, COUNT(*) AS total_scans,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM   scans
GROUP  BY risk_level;
```
"Normally, an aggregate function like `COUNT(*)` collapses rows into groups defined by `GROUP BY risk_level`.  
However, to calculate a percentage, we need the group count divided by the **grand total** across all groups.  
The window function clause `OVER ()` instructs MySQL to compute `SUM(COUNT(*))` across the entire result partition without collapsing the individual `risk_level` rows. This allows us to compute exact percentages in a single, efficient query without needing a subquery or temporary table."

---

### Question 10: How do you prevent SQL injection in your Python database layer?
**Model Answer:**  
"We completely eliminate the risk of SQL injection by strictly using **parameterized queries** through `mysql-connector-python`.  
We never concatenate or format user strings directly into SQL statements (e.g., no f-strings or `%` string interpolation).  
Instead, we pass SQL statements with `%s` parameter markers, and provide user data as a separate tuple to `cursor.execute(sql, (param1, param2))`. The database connector automatically escapes and quotes the parameters, ensuring input is treated purely as literal data and never as executable SQL code."

---

### Question 11: What is the difference between static and dynamic analysis, and why did you choose static?
**Model Answer:**  
"In cybersecurity:
- **Dynamic analysis** visits the URL, executes its JavaScript, follows HTTP redirects, and captures server responses. While thorough, it introduces significant danger: client malware infection, zero-day browser exploits, IP disclosure, and detection by attacker anti-crawler evasion mechanisms.
- **Static analysis** treats the URL string purely as passive text without establishing any network connection to the target server. It inspects structural anomalies (IP addresses, excessive subdomains, `@` symbols, punycode, credential keywords).  
We chose static analysis because it provides instant, zero-risk threat intelligence and safe educational demonstration without requiring network infrastructure or risking client safety."

---

### Question 12: How are Python data structures mapped to syllabus concepts in your codebase?
**Model Answer:**  
"In `core/` and `config.py`, we demonstrate all fundamental Python data structures:
- **Tuples:** Used for immutable configuration that must never change at runtime, such as `ALLOWED_SCHEMES = ('http', 'https')` and risk level threshold tuples.
- **Sets:** Used for $O(1)$ constant-time membership lookups, such as `SPECIAL_CHARACTERS = set('@~!$*()+[],;')` and suspicious URL shortener domains.
- **Dictionaries:** Used for key-value associative mappings, such as `RULE_WEIGHTS` and `RULE_INFO`.
- **Lists:** Used for ordered, dynamic collections, such as the evaluated list of `RuleResult` objects and scan history records."

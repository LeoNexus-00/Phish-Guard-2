-- ============================================================
-- PhishGuard — DBMS Demonstration Queries
-- Run: mysql -u root -p phishguard_db < database/queries.sql
-- ============================================================

USE phishguard_db;

-- ----------------------------------------------------------------
-- Query 1: Scan History
-- Concept: SELECT, ORDER BY, all rows
-- ----------------------------------------------------------------
SELECT scan_id, LEFT(url, 60) AS url_preview, risk_score, risk_level, scanned_at
FROM   scans
ORDER  BY scanned_at DESC;

-- ----------------------------------------------------------------
-- Query 2: Risk Distribution
-- Concept: GROUP BY, COUNT() aggregate function, window function
-- ----------------------------------------------------------------
SELECT   risk_level,
         COUNT(*)                                           AS total_scans,
         ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM     scans
GROUP BY risk_level
ORDER BY total_scans DESC;

-- ----------------------------------------------------------------
-- Query 3: Triggered-rule breakdown per scan
-- Concept: JOIN (scans ⋈ scan_rules ⋈ rules), WHERE filter
-- ----------------------------------------------------------------
SELECT s.scan_id,
       LEFT(s.url, 50)   AS url_preview,
       r.rule_name,
       sr.triggered,
       sr.points_awarded
FROM   scans      s
JOIN   scan_rules sr ON s.scan_id  = sr.scan_id
JOIN   rules      r  ON sr.rule_id = r.rule_id
WHERE  sr.triggered = TRUE
ORDER  BY s.scan_id DESC, sr.points_awarded DESC;

-- ----------------------------------------------------------------
-- Query 4: Most frequently triggered rules
-- Concept: JOIN, COUNT(), GROUP BY, ORDER BY, TOP-N pattern
-- ----------------------------------------------------------------
SELECT   r.rule_name,
         COUNT(*)               AS times_triggered,
         SUM(sr.points_awarded) AS total_points_awarded
FROM     scan_rules sr
JOIN     rules      r  ON sr.rule_id = r.rule_id
WHERE    sr.triggered = TRUE
GROUP BY r.rule_id, r.rule_name
ORDER BY times_triggered DESC
LIMIT    10;

-- ----------------------------------------------------------------
-- Query 5: Monthly analytics
-- Concept: DATE functions, GROUP BY year+month, multiple aggregates
-- ----------------------------------------------------------------
SELECT   YEAR(scanned_at)                   AS yr,
         MONTH(scanned_at)                  AS mo,
         COUNT(*)                           AS total_scans,
         ROUND(AVG(risk_score), 1)          AS avg_score,
         SUM(risk_level = 'Low Risk')       AS low_risk_count,
         SUM(risk_level = 'Suspicious')     AS suspicious_count,
         SUM(risk_level = 'High Suspicion') AS high_suspicion_count
FROM     scans
GROUP BY yr, mo
ORDER BY yr DESC, mo DESC;

-- ----------------------------------------------------------------
-- Query 6: Use the scan_summary view
-- Concept: CREATE VIEW (defined in schema.sql), SELECT from view
-- ----------------------------------------------------------------
SELECT * FROM scan_summary
WHERE  rules_triggered >= 3
ORDER  BY risk_score DESC;

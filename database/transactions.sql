-- ============================================================
-- PhishGuard — Transaction Demonstration (ACID Properties)
-- Demonstrates: START TRANSACTION, COMMIT, ROLLBACK, atomicity
-- Run manually inside a MySQL session:
--     mysql -u root -p phishguard_db < database/transactions.sql
-- ============================================================

USE phishguard_db;

-- ---------------------------------------------------------------
-- Demo A: Successful transaction (COMMIT)
-- ---------------------------------------------------------------
START TRANSACTION;

INSERT INTO scans (url, risk_score, risk_level)
VALUES ('http://demo-transaction-test.example.com/login', 55, 'Suspicious');

-- Save the new scan_id into a session variable
SET @demo_scan_id = LAST_INSERT_ID();

INSERT INTO scan_rules (scan_id, rule_id, triggered, points_awarded)
SELECT @demo_scan_id, rule_id, TRUE, weight
FROM   rules
WHERE  rule_code = 'https_check';

-- Everything succeeded — make all changes permanent
COMMIT;

SELECT 'Demo A committed successfully.' AS status_message;

-- ---------------------------------------------------------------
-- Demo B: Failed transaction (ROLLBACK)
-- Demonstrates Atomicity: either all operations persist or none do.
-- ---------------------------------------------------------------
START TRANSACTION;

INSERT INTO scans (url, risk_score, risk_level)
VALUES ('http://rollback-test.example.com', 80, 'High Suspicion');

SET @demo_scan_id2 = LAST_INSERT_ID();

-- Deliberately attempt an invalid insert (or simulate failure).
-- When an error occurs or condition fails, ROLLBACK restores the state:
ROLLBACK;

SELECT 'Demo B rolled back — no partial data was saved.' AS status_message;

-- Verify: the rollback-test URL should NOT appear in the table.
SELECT COUNT(*) AS should_be_zero
FROM   scans
WHERE  url LIKE '%rollback-test%';

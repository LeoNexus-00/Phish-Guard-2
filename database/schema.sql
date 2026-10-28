-- ============================================================
-- PhishGuard DB Schema — phishguard_db
-- Demonstrates: DDL, PK, FK, CHECK, composite PK, referential
--               integrity, ON DELETE CASCADE, VIEW, INDEX
-- ============================================================

CREATE DATABASE IF NOT EXISTS phishguard_db
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE phishguard_db;

-- Table A: scans
-- One row per URL analysis run.
CREATE TABLE IF NOT EXISTS scans (
    scan_id     INT           NOT NULL AUTO_INCREMENT,
    url         VARCHAR(2048) NOT NULL,
    risk_score  INT           NOT NULL,
    risk_level  VARCHAR(20)   NOT NULL,
    scanned_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_scans        PRIMARY KEY (scan_id),
    CONSTRAINT chk_score       CHECK (risk_score BETWEEN 0 AND 100),
    CONSTRAINT chk_risk_level  CHECK (risk_level IN ('Low Risk', 'Suspicious', 'High Suspicion')),
    INDEX idx_scans_time (scanned_at DESC)
);

-- Table B: rules
-- One row per heuristic rule definition seeded from Python config.
CREATE TABLE IF NOT EXISTS rules (
    rule_id    INT          NOT NULL AUTO_INCREMENT,
    rule_code  VARCHAR(50)  NOT NULL,   -- matches Python rule_id key, e.g. "ip_address"
    rule_name  VARCHAR(100) NOT NULL,
    weight     INT          NOT NULL,

    CONSTRAINT pk_rules       PRIMARY KEY (rule_id),
    CONSTRAINT uq_rule_code   UNIQUE (rule_code)
);

-- Table C: scan_rules (junction / fact table)
-- One row per (scan, rule) pair — records the outcome of every check.
CREATE TABLE IF NOT EXISTS scan_rules (
    scan_id        INT     NOT NULL,
    rule_id        INT     NOT NULL,
    triggered      BOOLEAN NOT NULL,
    points_awarded INT     NOT NULL DEFAULT 0,

    CONSTRAINT pk_scan_rules   PRIMARY KEY (scan_id, rule_id),   -- composite PK
    CONSTRAINT fk_sr_scan      FOREIGN KEY (scan_id)
        REFERENCES scans(scan_id) ON DELETE CASCADE,
    CONSTRAINT fk_sr_rule      FOREIGN KEY (rule_id)
        REFERENCES rules(rule_id) ON DELETE RESTRICT
);

-- View: restricted scan summary (no raw URL, no rule detail)
-- Demonstrates: CREATE VIEW, column aliasing, aggregation in view
CREATE OR REPLACE VIEW scan_summary AS
    SELECT
        s.scan_id,
        LEFT(s.url, 50)                          AS url_preview,
        s.risk_score,
        s.risk_level,
        s.scanned_at,
        COUNT(CASE WHEN sr.triggered THEN 1 END) AS rules_triggered
    FROM scans s
    LEFT JOIN scan_rules sr ON s.scan_id = sr.scan_id
    GROUP BY s.scan_id, s.url, s.risk_score, s.risk_level, s.scanned_at;

-- ============================================================
-- PhishGuard Seed Data — 18 Rules
-- Sourced directly from config.RULE_WEIGHTS and core/rule_engine.py
-- Safe to run multiple times: INSERT IGNORE skips duplicate rule_code.
-- ============================================================

USE phishguard_db;

INSERT IGNORE INTO rules (rule_code, rule_name, weight) VALUES
    ('https_check',         'HTTPS Check',                       10),
    ('ip_address',          'IP Address Hostname',                25),
    ('at_symbol',           '@ Symbol in Address',               20),
    ('suspicious_keywords', 'Suspicious Keywords',               10),
    ('keyword_in_domain',   'Keyword in Domain Name',            10),
    ('url_length',          'URL Length (long)',                  10),
    ('url_length_very_long','URL Length (very long)',             15),
    ('subdomains',          'Excessive Subdomains',              10),
    ('embedded_domain',     'Domain Name Inside Subdomain',      15),
    ('hyphens',             'Hyphenated Hostname',               10),
    ('special_characters',  'Special Character Patterns',        10),
    ('url_shortener',       'URL Shortener',                     10),
    ('punycode',            'Punycode / Look-alike Characters',  20),
    ('url_encoding',        'URL Encoding',                      10),
    ('suspicious_tld',      'Suspicious TLD',                    10),
    ('non_standard_port',   'Non-standard Port',                 10),
    ('hostname_digits',     'Digits in Hostname',                 5),
    ('ssl_certificate',     'SSL Certificate Check',             25);

# 🎯 PhishGuard Presentation & PPT Cheatsheet

Use this exact guide when preparing your presentation slides and viva demonstration.

---

## 📊 Recommended PPT Slide Structure (8 Slides Total)

### Slide 1: Title & Team
* **Project Title:** PhishGuard — Educational Rule-Based URL Security Analyzer
* **Course:** Introduction to Python Programming (Sem-3, Course Code: 102040306)
* **Team Members:** [Your Name] & [Your Friend's Name]
* **One-line Summary:** A pure Python static analysis engine that assesses URL risk without visiting or executing untrusted links.

---

### Slide 2: Problem Statement & Motivation
* **The Problem:** Phishing attacks are the #1 cause of credential theft and cyber fraud. Fake URLs imitate trusted brands (banks, PayPal, university portals).
* **The Risk of Visiting Links:** Typical users click the link to see if it's fake, exposing themselves to malware or credential capture.
* **Our Solution:** **Static Analysis**. Inspect the URL string safely like a detective without ever connecting to the malicious server.

---

### Slide 3: System Architecture & Workflow
Show this 5-step pipeline:
1. **Input Validation (`utils/validators.py`)** -> Cleans spaces, checks character sets, handles errors gracefully.
2. **URL Decomposition (`core/url_parser.py`)** -> Splits into scheme, subdomain, registered domain, path, query.
3. **Feature Extraction (`core/feature_extractor.py`)** -> Extracts 25+ measurable properties (lengths, symbols, keywords).
4. **Rule Engine (`core/rule_engine.py`)** -> Evaluates 16 weighted security rules and assigns risk points.
5. **Scoring & Output (`core/risk_calculator.py`)** -> Computes final score (0–100) and displays report (CLI or Web).

---

### Slide 4: Code Implementation: Data Structures (Unit 5)
*Show this snippet in your slide:*
```python
# 1. TUPLES (Immutable config)
ALLOWED_SCHEMES = ("http", "https")

# 2. SETS (O(1) fast lookup for symbols and shorteners)
SPECIAL_CHARACTERS = set("@~!$*()+[],;'")

# 3. DICTIONARIES (Key-value rule weights)
RULE_WEIGHTS = {
    "ip_address": 25,
    "at_symbol": 20,
    "https_check": 10
}

# 4. LISTS (Ordered collection of triggered rules)
triggered_rules = [rule for rule in all_rules if rule.triggered]
```
* **Viva Explanation:** "We used Tuples for constants, Sets for high-speed membership testing, Dictionaries for weighted scoring, and Lists for collecting flagged rules."

---

### Slide 5: Code Implementation: OOP & Exception Handling (Unit 6)
*Show this snippet in your slide:*
```python
# Custom Exception class
class InvalidURLError(ValueError):
    """Raised when a URL fails validation."""
    pass

# Object-Oriented Programming (Class with Constructor)
class URLAnalyzer:
    def __init__(self):
        self.extractor = FeatureExtractor(...)
        self.rule_engine = RuleEngine()

    def analyze(self, raw_url):
        try:
            url, notes = validate_url(raw_url)
            features = self.extractor.extract(url)
            return self.rule_engine.evaluate_rules(features)
        except InvalidURLError as err:
            print(f"Safe error handling: {err}")
```
* **Viva Explanation:** "We defined custom exception `InvalidURLError` so the program never crashes on bad input, and encapsulated our entire detection logic into modular classes."

---

### Slide 6: Key Detection Rules (The "Meat" of the Project)
Highlight 4 high-impact rules:
1. **IP Address Hostname:** Flags raw IP addresses (`http://192.168.1.1/login`) used to bypass domain reputation.
2. **`@` Symbol Disguise:** Flags `http://google.com@evil-site.com` where browsers ignore the text before `@`.
3. **Suspicious Keyword Matching:** Categorized matching for credentials (`login`, `verify`, `account`, `bank`).
4. **Embedded Subdomains:** Flags `paypal.com.account-update.net` where trusted names fool human eyes.

---

### Slide 7: Project Demo & Output
* Put 2 screenshots:
  1. Terminal CLI output showing a flagged scan.
  2. Streamlit Web UI showing the colored risk gauge and dashboard.

---

### Slide 8: Conclusion & Future Scope
* **Conclusion:** 100% built using Python standard library fundamentals without relying on third-party APIs.
* **Future Scope:**
  - Machine Learning classifier trained on the exact same feature dictionary.
  - Browser extension integration for real-time link hover warning.

---

## 🎬 Live Viva Demo Plan (2 Minutes)

1. **Step 1:** Open terminal and run:
   ```bash
   python cli.py
   ```
2. **Step 2:** Test a **Safe URL**:
   ```text
   https://www.google.com
   ```
   *Score: 0/100 (Low Risk)*
3. **Step 3:** Test an **Unsafe Phishing URL**:
   ```text
   http://198.51.100.7/secure-bank-login/verify-account.php
   ```
   *Score: 70+/100 (High Suspicion)*
   *Point out to examiner:* "Sir, notice how it caught the raw IP address, the missing HTTPS encryption, and the suspicious financial keywords!"

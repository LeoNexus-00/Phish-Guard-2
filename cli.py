"""
cli.py - A simple command-line version of PhishGuard.

Usage:
    python cli.py                      (interactive mode)
    python cli.py "http://example.com" (analyse one URL)

The CLI does NOT save scans to the history; it is useful for quick testing
and for demonstrating the core logic without the web interface.
"""

import sys

from core.analyzer import URLAnalyzer
from utils.helpers import format_text_report
from utils.validators import InvalidURLError


def analyse_and_print(analyzer, raw_url):
    """Analyse one URL and print the report (or a friendly error)."""
    try:
        result = analyzer.analyze(raw_url)
        print(format_text_report(result))

        # Save to MySQL database
        try:
            from services.scan_repository import ScanRepository
            scan_id = ScanRepository().save_scan(result)
            print(f"[DB] Scan saved to MySQL (scan_id: {scan_id}).")
        except RuntimeError as err:
            print(f"[DB] {err}")
        except Exception as err:
            print(f"[DB] Could not save to MySQL: {err}")
    except InvalidURLError as error:
        print(f"Invalid input: {error}")


def main():
    # Windows consoles may not support every character (e.g. non-English
    # letters in a URL). Replace unprintable characters instead of crashing.
    sys.stdout.reconfigure(errors="replace")
    analyzer = URLAnalyzer()

    # Mode 1: URLs given as command-line arguments.
    if len(sys.argv) > 1:
        for raw_url in sys.argv[1:]:
            analyse_and_print(analyzer, raw_url)
        return

    # Mode 2: interactive loop.
    print("PhishGuard - static URL risk analysis (type 'q' to quit)")
    while True:
        try:
            raw_url = input("\nEnter a URL: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if raw_url.strip().lower() in ("q", "quit", "exit"):
            break
        analyse_and_print(analyzer, raw_url)
    print("Goodbye!")


if __name__ == "__main__":
    main()

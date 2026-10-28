"""
services/scan_repository.py - MySQL persistence repository for PhishGuard.

All SQL database operations are encapsulated in this class.
No SQL appears in app.py, cli.py, or other modules.

Transaction Guarantee:
    save_scan() writes the header to `scans` and all individual check
    outcomes to `scan_rules` inside a single ACID transaction. On any
    failure, the entire operation is rolled back, preventing orphaned
    or partial records.
"""

from database.connection import get_connection


class ScanRepository:
    """Manages database operations for scans, rules, and statistics."""

    # ------------------------------------------------------------------
    # Write Operations
    # ------------------------------------------------------------------
    def save_scan(self, result):
        """
        Persist a URLResult and all of its rule checks to MySQL.

        Args:
            result (URLResult): The full analysis result from URLAnalyzer.

        Returns:
            int: The generated AUTO_INCREMENT scan_id.

        Raises:
            RuntimeError: If connection fails or an error occurs during execution.
        """
        connection = get_connection()
        cursor = connection.cursor()
        try:
            # 1. Insert header row into `scans`
            cursor.execute(
                """
                INSERT INTO scans (url, risk_score, risk_level)
                VALUES (%s, %s, %s)
                """,
                (result.url, int(result.risk_score), str(result.risk_level)),
            )
            scan_id = cursor.lastrowid

            # 2. Resolve rule_code -> rule_id from `rules` table
            cursor.execute("SELECT rule_id, rule_code FROM rules")
            rule_map = {code: r_id for r_id, code in cursor.fetchall()}

            # 3. Insert each evaluated rule into `scan_rules`
            for rule_result in result.rule_results:
                rule_code = rule_result.rule_id
                # Handle distinction between normal long URL and very long URL
                if rule_code == "url_length" and int(rule_result.score) >= 15:
                    db_rule_id = rule_map.get("url_length_very_long") or rule_map.get("url_length")
                else:
                    db_rule_id = rule_map.get(rule_code)

                if db_rule_id is None:
                    # Gracefully skip if rule definition not yet seeded in DB
                    continue

                cursor.execute(
                    """
                    INSERT INTO scan_rules (scan_id, rule_id, triggered, points_awarded)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        scan_id,
                        db_rule_id,
                        bool(rule_result.triggered),
                        int(rule_result.score),
                    ),
                )

            # 4. Commit atomic transaction
            connection.commit()
            return scan_id

        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    # ------------------------------------------------------------------
    # Read Operations
    # ------------------------------------------------------------------
    def load_history(self, limit=500):
        """
        Fetch recent scans from MySQL ordered by newest first.

        Returns:
            list[dict]: List of scan dictionaries.
        """
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    s.scan_id,
                    s.url,
                    s.risk_score,
                    s.risk_level,
                    DATE_FORMAT(s.scanned_at, '%Y-%m-%d %H:%i:%s') AS scanned_at,
                    COUNT(CASE WHEN sr.triggered THEN 1 END)       AS indicators_count
                FROM scans s
                LEFT JOIN scan_rules sr ON s.scan_id = sr.scan_id
                GROUP BY s.scan_id, s.url, s.risk_score, s.risk_level, s.scanned_at
                ORDER BY s.scanned_at DESC, s.scan_id DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

    def get_scan_details(self, scan_id):
        """
        Retrieve complete information for a specific scan, including triggered rules.

        Returns:
            dict or None: Detailed scan information.
        """
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT
                    scan_id,
                    url,
                    risk_score,
                    risk_level,
                    DATE_FORMAT(scanned_at, '%Y-%m-%d %H:%i:%s') AS scanned_at
                FROM scans
                WHERE scan_id = %s
                """,
                (scan_id,),
            )
            scan = cursor.fetchone()
            if not scan:
                return None

            cursor.execute(
                """
                SELECT
                    r.rule_code,
                    r.rule_name,
                    sr.triggered,
                    sr.points_awarded
                FROM scan_rules sr
                JOIN rules r ON sr.rule_id = r.rule_id
                WHERE sr.scan_id = %s
                ORDER BY sr.points_awarded DESC, r.rule_name ASC
                """,
                (scan_id,),
            )
            scan["rules"] = cursor.fetchall()
            return scan
        finally:
            cursor.close()
            connection.close()

    def get_statistics(self):
        """
        Compute aggregate statistics directly via SQL queries.

        Returns:
            dict: Aggregated analytics containing total scans, averages,
                  counts by risk category, and most common triggered indicators.
        """
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            # 1. Total count & average score
            cursor.execute(
                """
                SELECT
                    COUNT(*)         AS total_scans,
                    AVG(risk_score)  AS avg_score
                FROM scans
                """
            )
            totals = cursor.fetchone() or {"total_scans": 0, "avg_score": 0}

            # 2. Counts grouped by risk level
            cursor.execute(
                """
                SELECT risk_level, COUNT(*) AS count
                FROM scans
                GROUP BY risk_level
                """
            )
            level_rows = cursor.fetchall()

            # 3. Top triggered indicators via JOIN
            cursor.execute(
                """
                SELECT
                    r.rule_name,
                    COUNT(*) AS times_triggered
                FROM scan_rules sr
                JOIN rules r ON sr.rule_id = r.rule_id
                WHERE sr.triggered = TRUE
                GROUP BY r.rule_id, r.rule_name
                ORDER BY times_triggered DESC
                LIMIT 10
                """
            )
            top_rules = cursor.fetchall()

            # 4. Highest-risk scan
            cursor.execute(
                """
                SELECT
                    scan_id,
                    url,
                    risk_score,
                    risk_level,
                    DATE_FORMAT(scanned_at, '%Y-%m-%d %H:%i:%s') AS scanned_at
                FROM scans
                ORDER BY risk_score DESC, scanned_at DESC
                LIMIT 1
                """
            )
            highest_scan = cursor.fetchone()

            level_counts = {
                "Low Risk": 0,
                "Suspicious": 0,
                "High Suspicion": 0,
            }
            for row in level_rows:
                if row["risk_level"] in level_counts:
                    level_counts[row["risk_level"]] = row["count"]

            return {
                "total_scans":   int(totals["total_scans"] or 0),
                "average_score": round(float(totals["avg_score"] or 0), 1),
                "level_counts":  level_counts,
                "top_rules":     top_rules,
                "highest_scan":  highest_scan,
            }
        finally:
            cursor.close()
            connection.close()

    # ------------------------------------------------------------------
    # Delete Operations
    # ------------------------------------------------------------------
    def delete_scan(self, scan_id):
        """
        Delete a single scan.
        ON DELETE CASCADE automatically removes its entries from scan_rules.

        Returns:
            bool: True if row was deleted, False otherwise.
        """
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM scans WHERE scan_id = %s", (scan_id,))
            connection.commit()
            return cursor.rowcount > 0
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

    def clear_history(self):
        """
        Remove all scan records.

        Returns:
            bool: True on success.
        """
        connection = get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM scans")
            connection.commit()
            return True
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
            connection.close()

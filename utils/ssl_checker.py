"""
ssl_checker.py - Checks the SSL/TLS certificate of a website.

WHY THIS MODULE EXISTS
----------------------
PhishGuard normally does *static* text analysis: it looks at the URL string and
never connects to the internet.  However, one important real-world signal that
pure text analysis can never detect is a **bad or expired SSL certificate**.

Chrome shows "Your connection isn't private" when a certificate is expired,
self-signed, or issued for a different domain.  This module adds an OPTIONAL
live check so PhishGuard can detect such problems too.

HOW IT WORKS
------------
1. Open a TCP connection to the website on port 443 (HTTPS port).
2. Perform the SSL/TLS handshake and ask the server for its certificate.
3. Python's ssl library validates the certificate automatically:
   - Is it expired?  -> ssl.SSLCertVerificationError
   - Is it self-signed?  -> ssl.SSLCertVerificationError
   - Does the hostname match?  -> ssl.SSLCertVerificationError
4. If the handshake succeeds, read the expiry date from the certificate.
5. Return a simple dictionary with the results.

IMPORTANT: This module only reads the certificate. It does NOT download any
web page content, does NOT run any JavaScript, and does NOT send any user data.

Python concepts used:
    - try / except (multiple exception types)
    - Importing standard library modules (ssl, socket)
    - datetime parsing
    - Dictionary return value
"""

import socket
import ssl
from datetime import datetime, timezone


def check_ssl_certificate(hostname, port=443, timeout=5):
    """Check whether the SSL certificate of a hostname is valid.

    Args:
        hostname (str): the domain name to check, e.g. "utsav.gov.in".
        port (int): the port to connect to (443 is the HTTPS standard).
        timeout (int): seconds to wait before giving up.

    Returns:
        dict with the following keys:
            valid (bool or None):
                True  = certificate is valid and current.
                False = certificate failed verification (expired, wrong host, etc.).
                None  = could not connect (network error, DNS failure, etc.).
            error (str): human-readable error message (empty if valid).
            expires (str): certificate expiry date string (empty if unknown).
            days_remaining (int or None): days until expiry (negative = already expired).
            issuer (str): organisation that issued the certificate.
    """
    result = {
        "valid": None,
        "error": "",
        "expires": "",
        "days_remaining": None,
        "issuer": "",
    }

    # Step 1: Try with STRICT verification (the normal, safe way).
    try:
        context = ssl.create_default_context()                  # strict by default
        with socket.create_connection((hostname, port), timeout=timeout) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=hostname) as secure_socket:
                cert = secure_socket.getpeercert()

                # Certificate passed verification!
                result["valid"] = True
                _read_cert_details(cert, result)
                return result

    except ssl.SSLCertVerificationError as error:
        # Certificate exists but FAILED verification (expired, self-signed, etc.)
        result["valid"] = False
        result["error"] = _simplify_ssl_error(str(error))

        # Step 2: Connect AGAIN without verification just to read the expiry date.
        # This is safe: we still don't download any page content.
        _read_cert_without_verification(hostname, port, timeout, result)
        return result

    except (socket.timeout, socket.gaierror) as error:
        # DNS resolution failed or server did not respond in time.
        result["valid"] = None
        result["error"] = f"Could not connect to {hostname}: {error}"
        return result

    except (ConnectionRefusedError, ConnectionResetError, OSError) as error:
        # Server refused the connection or network is unreachable.
        result["valid"] = None
        result["error"] = f"Connection failed: {error}"
        return result


# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------

def _read_cert_details(cert, result):
    """Extract expiry date and issuer from a certificate dictionary."""
    not_after = cert.get("notAfter", "")
    if not_after:
        try:
            expire_date = ssl.cert_time_to_seconds(not_after)
            expire_dt = datetime.fromtimestamp(expire_date, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            result["expires"] = expire_dt.strftime("%Y-%m-%d %H:%M UTC")
            result["days_remaining"] = (expire_dt - now).days
        except (ValueError, OSError):
            result["expires"] = not_after

    issuer = cert.get("issuer", ())
    for field_group in issuer:
        for key, value in field_group:
            if key == "organizationName":
                result["issuer"] = value
                return


def _read_cert_without_verification(hostname, port, timeout, result):
    """Connect without verification to read the certificate details.

    This is used ONLY when we already know the cert is invalid and want to
    show the user when it expired or who issued it.
    """
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((hostname, port), timeout=timeout) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=hostname) as secure_socket:
                # getpeercert() returns {} when verify_mode is CERT_NONE,
                # but getpeercert(binary_form=True) still works.
                der_cert = secure_socket.getpeercert(binary_form=True)
                if der_cert:
                    pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
                    # Decode using the ssl module
                    cert = ssl._ssl._test_decode_cert(pem_cert)  # noqa
                    if cert:
                        _read_cert_details(cert, result)
    except Exception:
        # If this fallback also fails, we just don't have the extra details.
        pass


def _simplify_ssl_error(error_text):
    """Turn a technical SSL error into a readable sentence."""
    lower = error_text.lower()
    if "certificate has expired" in lower or "cert_has_expired" in lower:
        return "The SSL certificate has expired (the website's security pass is out of date)."
    if "self-signed" in lower or "self_signed" in lower:
        return "The SSL certificate is self-signed (not issued by a trusted authority)."
    if "hostname mismatch" in lower:
        return "The SSL certificate was issued for a different domain name."
    if "unable to get local issuer" in lower:
        return "The SSL certificate's issuer is not recognised as trusted."
    # Fallback: return the original message cleaned up.
    return f"SSL certificate error: {error_text}"

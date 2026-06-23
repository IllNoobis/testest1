"""
license_check.py — Called by start_servers.ps1 to verify license.
Also supports --activate KEY to activate from command line.
Exits with code 0 if valid, 1 if invalid/missing.
"""
import os
import sys
from license_manager import LicenseManager, LicenseError

def main():
    server_url = os.environ.get("LICENSE_SERVER_URL", "").strip()
    if not server_url:
        print("[LICENSE] No license server configured — skipping check")
        sys.exit(0)

    lm = LicenseManager(server_url)

    # Handle --activate flag
    if "--activate" in sys.argv:
        idx = sys.argv.index("--activate") + 1
        if idx < len(sys.argv):
            key = sys.argv[idx].strip()
            try:
                result = lm.activate(key)
                if result.get("success"):
                    print(f"[LICENSE] Activated! Expires: {result.get('expires_at', 'unknown')}")
                    sys.exit(0)
                else:
                    print(f"[LICENSE] Activation failed: {result.get('message', 'Unknown error')}")
                    sys.exit(1)
            except LicenseError as e:
                print(f"[LICENSE] Activation error: {e}")
                sys.exit(1)
        else:
            print("[LICENSE] Usage: py license_check.py --activate YOUR-KEY")
            sys.exit(1)

    if not lm.is_activated:
        print("[LICENSE] NOT ACTIVATED")
        print(f"[LICENSE] Your HWID: {lm.get_hwid_display()}")
        print(f"[LICENSE] To activate: py license_check.py --activate YOUR-KEY")
        sys.exit(1)

    valid, days, msg = lm.validate()
    if valid:
        print(f"[LICENSE] Valid — {days} days remaining ({msg})")
        sys.exit(0)
    else:
        print(f"[LICENSE] INVALID: {msg}")
        sys.exit(1)

if __name__ == "__main__":
    main()

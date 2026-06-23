"""
license_check.py — Called by start_servers.ps1 to verify license.
Also supports --activate KEY to activate from command line.
Exits with code 0 if valid, 1 if invalid/missing.
"""
import json
import os
import sys
from pathlib import Path
from license_manager import LicenseManager, LicenseError

_CONFIG_FILE = Path(__file__).parent / "bridge_config.json"


def _get_server_url() -> str:
    """Read server URL from env var, then bridge_config.json, then default."""
    url = os.environ.get("LICENSE_SERVER_URL", "").strip()
    if url:
        return url
    try:
        cfg = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        url = (cfg.get("license") or {}).get("server_url", "").strip()
        if url:
            return url
    except Exception:
        pass
    return ""


def main():
    server_url = _get_server_url()
    if not server_url:
        print("[LICENSE] No license server configured — skipping check")
        sys.exit(0)

    lm = LicenseManager(server_url)

    # Handle --activate flag
    if "--activate" in sys.argv:
        idx = sys.argv.index("--activate") + 1
        if idx < len(sys.argv):
            key = sys.argv[idx].strip()
            print(f"[LICENSE] Activating on server: {server_url}")
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

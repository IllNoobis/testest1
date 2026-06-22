"""
license_manager.py — Client-side license validation for the bridge.
HWID generation, server validation, periodic check-ins.

Can be compiled to .pyd with Cython for tamper resistance.
See compile_license.py in this directory.
"""

import hashlib
import json
import platform
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None  # Will fail gracefully with a message

LICENSE_FILE = Path(__file__).parent / ".license"
SERVER_URL = "http://localhost:9876"  # CHANGE THIS to your server URL

CHECK_INTERVAL = 3600  # Re-check every hour while bridge runs


def get_hwid() -> str:
    """Generate a unique machine identifier."""
    parts = []
    # Motherboard serial (Windows)
    try:
        out = subprocess.check_output(
            "wmic baseboard get serialnumber", shell=True, stderr=subprocess.DEVNULL
        ).decode().strip().split("\n")[-1].strip()
        if out and "default" not in out.lower():
            parts.append(out)
    except Exception:
        pass
    # Disk serial
    try:
        out = subprocess.check_output(
            "wmic diskdrive get serialnumber", shell=True, stderr=subprocess.DEVNULL
        ).decode().strip().split("\n")[-1].strip()
        if out:
            parts.append(out)
    except Exception:
        pass
    # MAC address
    try:
        import hashlib as h
        mac = uuid.getnode()
        if mac:
            parts.append(f"{mac:012x}")
    except Exception:
        pass
    # Fallback: hostname + python path
    if not parts:
        parts.append(platform.node())
        parts.append(sys.prefix)
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()


class LicenseError(Exception):
    pass


class LicenseManager:
    def __init__(self, server_url: str = None):
        self.server_url = (server_url or SERVER_URL).rstrip("/")
        self.hwid = get_hwid()
        self._last_check = 0
        self._valid = False
        self._expires_at = ""
        self._days_remaining = 0

    @property
    def is_activated(self) -> bool:
        """Check if a license file exists locally."""
        return LICENSE_FILE.exists()

    def _load_local(self) -> dict:
        if not LICENSE_FILE.exists():
            return {}
        try:
            data = json.loads(LICENSE_FILE.read_text())
            return data
        except Exception:
            return {}

    def _save_local(self, data: dict):
        LICENSE_FILE.write_text(json.dumps(data, indent=2))

    def get_hwid_display(self) -> str:
        """Show HWID in chunks for easy reading."""
        h = self.hwid
        return "-".join(h[i:i+4] for i in range(0, len(h), 4))

    def activate(self, license_key: str) -> dict:
        """Activate a license key against the server."""
        if not requests:
            raise LicenseError("requests library required: pip install requests")
        try:
            resp = requests.post(
                f"{self.server_url}/register",
                json={"license_key": license_key.strip().upper(), "hwid": self.hwid},
                timeout=10,
            )
            data = resp.json()
            if data.get("success"):
                self._save_local({
                    "license_key": license_key.strip().upper(),
                    "hwid": self.hwid,
                    "expires_at": data["expires_at"],
                    "activated_at": datetime.now(timezone.utc).isoformat(),
                })
                self._valid = True
                self._expires_at = data["expires_at"]
            return data
        except requests.exceptions.ConnectionError:
            raise LicenseError(f"Cannot reach license server: {self.server_url}")
        except Exception as e:
            raise LicenseError(f"Activation failed: {e}")

    def validate(self) -> tuple:
        """
        Returns (is_valid: bool, days_remaining: int, message: str).
        First checks local cache, then phones home periodically.
        """
        local = self._load_local()
        if not local:
            return False, 0, "Not activated"

        # Always check expiration from local data first
        expires_str = local.get("expires_at", "")
        if expires_str:
            try:
                expires = datetime.fromisoformat(expires_str)
                remaining = (expires - datetime.now(timezone.utc)).days
                if expires < datetime.now(timezone.utc):
                    return False, 0, "License expired"
            except Exception:
                pass

        # Phone home periodically
        now = time.time()
        if now - self._last_check > CHECK_INTERVAL:
            self._last_check = now
            if requests:
                try:
                    resp = requests.post(
                        f"{self.server_url}/validate",
                        json={"license_key": local.get("license_key", ""), "hwid": self.hwid},
                        timeout=10,
                    )
                    data = resp.json()
                    if data.get("valid"):
                        self._valid = True
                        self._expires_at = data.get("expires_at", expires_str)
                        self._days_remaining = data.get("days_remaining", 0)
                        return True, self._days_remaining, "Valid"
                    else:
                        return False, 0, data.get("message", "Server rejected license")
                except requests.exceptions.ConnectionError:
                    # Server unreachable - use local cache
                    pass
                except Exception:
                    pass

        # Fallback: use cached data
        if expires_str:
            try:
                expires = datetime.fromisoformat(expires_str)
                remaining = (expires - datetime.now(timezone.utc)).days
                if remaining >= 0:
                    return True, remaining, "Valid (cached)"
                return False, 0, "License expired"
            except Exception:
                pass

        return True, 30, "Could not verify (offline mode)"

    def deactivate_local(self):
        """Remove local license file."""
        if LICENSE_FILE.exists():
            LICENSE_FILE.unlink()
        self._valid = False


if __name__ == "__main__":
    lm = LicenseManager()
    action = sys.argv[1] if len(sys.argv) > 1 else "status"

    if action == "hwid":
        print(f"HWID: {lm.get_hwid_display()}")
    elif action == "activate":
        if len(sys.argv) < 3:
            print("Usage: python license_manager.py activate LICENSE-KEY")
            sys.exit(1)
        key = sys.argv[2]
        try:
            result = lm.activate(key)
            if result.get("success"):
                print(f"[+] Activated! Expires: {result.get('expires_at', 'unknown')}")
            else:
                print(f"[-] Failed: {result.get('message', 'Unknown error')}")
        except LicenseError as e:
            print(f"[-] {e}")
    elif action == "status":
        valid, days, msg = lm.validate()
        if valid:
            print(f"[+] License valid. {days} days remaining. ({msg})")
        else:
            print(f"[-] License invalid: {msg}")
        print(f"    HWID: {lm.get_hwid_display()}")
    elif action == "deactivate":
        lm.deactivate_local()
        print("[-] Local license removed")
    else:
        print("Usage: python license_manager.py [hwid|activate|status|deactivate]")

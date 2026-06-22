"""
gen_license.py — Generate license keys for your customers.

Usage:
  python gen_license.py --days 30 "CustomerName"
  python gen_license.py --days 365 --hwid ABC123 "CustomerName"
  python gen_license.py --list
  python gen_license.py --deactivate LICENSE-KEY
"""

import sqlite3
import secrets
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "licenses.db"


def _init_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            license_key TEXT PRIMARY KEY,
            hwid TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            last_checkin TEXT,
            note TEXT
        )
    """)
    conn.commit()
    conn.close()


def _format_key(raw: str) -> str:
    raw = raw.upper()[:20]
    return "-".join(raw[i:i+5] for i in range(0, len(raw), 5))


def _generate():
    raw = secrets.token_hex(10)
    return _format_key(raw)


def create_license(days: int, note: str = "", hwid: str = ""):
    _init_db()
    key = _generate()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=days)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO licenses (license_key, hwid, created_at, expires_at, active, note) VALUES (?, ?, ?, ?, 1, ?)",
        (key, hwid, now.isoformat(), expires.isoformat(), note),
    )
    conn.commit()
    conn.close()
    print(f"[+] License created: {key}")
    print(f"    Expires: {expires.isoformat()} ({days} days)")
    print(f"    Customer: {note}")
    if hwid:
        print(f"    Pre-bound HWID: {hwid}")
    return key


def list_licenses():
    _init_db()
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT license_key, hwid, created_at, expires_at, active, last_checkin, note FROM licenses ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    if not rows:
        print("No licenses found.")
        return
    print(f"{'LICENSE KEY':<25} {'HWID':<16} {'ACTIVE':<7} {'EXPIRES':<25} {'LAST CHECKIN':<25} {'NOTE'}")
    print("-" * 120)
    for r in rows:
        active = "YES" if r[4] else "NO"
        hwid_short = (r[1] or "-")[:14]
        print(f"{r[0]:<25} {hwid_short:<16} {active:<7} {r[3][:19]:<25} {(r[5] or '-')[:19]:<25} {r[6] or ''}")


def deactivate(key: str):
    _init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("UPDATE licenses SET active = 0 WHERE license_key = ?", (key.strip().upper(),))
    conn.commit()
    affected = conn.total_changes
    conn.close()
    if affected:
        print(f"[-] Deactivated: {key}")
    else:
        print(f"[!] License not found: {key}")


if __name__ == "__main__":
    _init_db()
    if "--list" in sys.argv:
        list_licenses()
    elif "--deactivate" in sys.argv:
        idx = sys.argv.index("--deactivate") + 1
        if idx < len(sys.argv):
            deactivate(sys.argv[idx])
        else:
            print("Usage: python gen_license.py --deactivate LICENSE-KEY")
    elif "--days" in sys.argv:
        idx = sys.argv.index("--days") + 1
        days = int(sys.argv[idx]) if idx < len(sys.argv) else 30
        hwid = ""
        note = ""
        if "--hwid" in sys.argv:
            hidx = sys.argv.index("--hwid") + 1
            if hidx < len(sys.argv):
                hwid = sys.argv[hidx].strip()
        # Everything after the flags is the customer note
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        if args:
            params = []
            skip = False
            for a in sys.argv[1:]:
                if skip:
                    skip = False
                    continue
                if a == "--days":
                    skip = True
                elif a == "--hwid":
                    skip = True
                elif not a.startswith("--"):
                    params.append(a)
            note = " ".join(params)
        create_license(days, note, hwid)
    else:
        print("Usage:")
        print("  python gen_license.py --days 30 'CustomerName'")
        print("  python gen_license.py --days 365 --hwid ABC123 'CustomerName'")
        print("  python gen_license.py --list")
        print("  python gen_license.py --deactivate LICENSE-KEY")

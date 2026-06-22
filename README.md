# Deepchart CQG/Rithmic Proxy Toolkit

This tool lets you use **Deepchart** with either **CQG** (AMP demo account) or **Rithmic** (free trial, no broker needed).
It runs a man-in-the-middle proxy that sits between Deepchart and your data source, inspecting and modifying the traffic between them.

The primary focus of this project is **Rithmic mode**, where the bridge translates CQG protocol from Deepchart into Rithmic Protocol API calls locally, eliminating the need for a CQG broker account.

---

## Prerequisites

- **Windows** (Deepchart only runs on Windows)
- **Python 3.11.15** installed with a virtual environment (see below)
- **Either:** a CQG trading account (AMP demo) **or** a Rithmic free trial account
- **Deepchart** already installed
- **Administrator access** (required to bind to port 443)

### Python Version

The project uses a Python 3.11.15 virtual environment (`.venv311`). This is required because `protobuf<5` (a dependency of `async_rithmic`) is incompatible with Python 3.14.

When `RITHMIC_MODE` is set, `start_servers.ps1` automatically activates the `.venv311` virtual environment. For CQG mode, any recent Python version works.

---

## Setup

### 1. Install Python 3.11

Download Python 3.11.15 from https://www.python.org/downloads/release/python-31115/ and install it. Check **"Add Python to PATH"** during install if you want it available system-wide, or install alongside other versions.

### 2. Create the Virtual Environment

From the project directory in PowerShell:

```powershell
python -m venv .venv311
.\.venv311\Scripts\Activate.ps1
pip install -r requirements.txt
pip install async_rithmic
```

### 3. Redirect Traffic to Your Machine

Run `toggle-proxy-hosts.bat` **as Administrator** to add the required hosts file entries. This redirects CQG and Rithmic traffic to your local machine so the proxy can intercept it.

The hosts file will redirect:
- `demoapi.cqg.com` and `api.cqg.com` to your machine
- `depth-it.historical.deepcharts.com` and `data-b.historical.deepcharts.com` to your machine
- `rituz00100.rithmic.com` to your machine (Rithmic mode)

Run the same file again to remove the entries when you need MotiveWave or QuantTower with AMP/CQG.

### 4. Install the Security Certificate (One-Time)

The proxy generates its own CA certificate to decrypt traffic. You must trust it:

1. Open the `mitm_ca` folder (run the proxy once if it does not exist yet).
2. Right-click `ca.pem` and select **Install Certificate**.
3. Choose **Local Machine**, then **Place all certificates in the following store**.
4. Browse to **Trusted Root Certification Authorities** and confirm.

### 5. Connect Deepchart

In Deepchart, go to **Connections > Add New > Data Feed: CQG**.

- **CQG mode:** Check "Use demo credentials" and enter your AMP CQG demo username and password.
- **Rithmic mode:** Enter your Rithmic trial username and password. Deepchart still speaks CQG protocol; the bridge translates it to Rithmic behind the scenes.

---

## Rithmic Mode

Rithmic offers a 14-day free paper trading account with no broker required. Sign up at https://rithmic.com.

### Configuration

Set the following environment variables before starting the servers:

```powershell
$env:RITHMIC_MODE = "1"
$env:RITHMIC_USER = "your_rithmic_username"
$env:RITHMIC_PASSWORD = "your_rithmic_password"
```

Optionally set `RITHMIC_SYSTEM` (defaults to `RithmicPaperTradingChicago`).

Then run:

```powershell
.\start_servers.ps1
```

The script detects `RITHMIC_MODE` and automatically uses the `.venv311` virtual environment with Python 3.11.

### How It Works

When `RITHMIC_MODE=1`, the bridge does not forward your connection to CQG servers. Instead, it runs the Rithmic translator locally. Deepchart believes it is talking to CQG and receives symbol resolution, real-time ticks, and market data, all translated from the Rithmic Protocol API.

### Switching Back to CQG Mode

```powershell
$env:RITHMIC_MODE = "0"
```

Or simply do not set the variable.

---

## Known Issues

This project is **not fully functional yet**. The Rithmic translation layer has several incomplete components. See [`issues.md`](issues.md) for the full list of fixed and outstanding issues.

Key current limitations:

- The Rithmic translator cannot yet deliver translated tick data back to Deepchart clients (no transport layer wired up)
- L2 (level 2) book data from Rithmic is not handled correctly
- Historical data handlers (TimeAndSales, TimeBar) are stubs that return empty responses
- Time and sales / bar chart features will not work in Rithmic mode until these are implemented
- The bridge requires Administrator privileges to bind to port 443

---

## What Each File Does

| File | Purpose |
|------|---------|
| `bridge_mitm_proxy.py` | Main proxy; CQG mode forwards to AMP, Rithmic mode translates locally |
| `rithmic_translator.py` | CQG-to-Rithmic protocol translator (used only in Rithmic mode) |
| `vol_hist_server.py` | Handles historical chart data requests |
| `ipc_mitm.py` | Optional monitor for Deepchart-to-bridge communication |
| `run_patched_deepchart.ps1` | Launches Deepchart with required patches |
| `mitm_ca/` | Security certificates (auto-created on first run) |
| `cqg_test/` | CQG protobuf definitions used by the proxy |
| `logs/` | Log files (auto-created) |
| `requirements.txt` | Python package dependencies |
| `toggle-proxy-hosts.bat` | Toggles hosts file entries on/off (run as admin) |
| `toggle-proxy-hosts.ps1` | PowerShell version of the hosts toggle |
| `start_servers.ps1` | Starts all services (run as admin) |

---

## Troubleshooting

### "Permission denied" or "Can't bind to port 443"
Run PowerShell as Administrator.

### "Python is not recognized"
Ensure Python 3.11 is installed and added to PATH, or that the `.venv311` virtual environment is activated.

### "No module named..."
Run `pip install -r requirements.txt` inside the activated `.venv311` environment.

### Bridge starts but Rithmic translator fails
Verify that:
- Python 3.11.15 is installed
- `pip install async_rithmic` was run inside `.venv311`
- `RITHMIC_USER` and `RITHMIC_PASSWORD` environment variables are set

### Deepchart connects but no data shows
Your hosts file may have an incorrect IP. Re-run `toggle-proxy-hosts.bat` as Administrator.

### The proxy starts but Deepchart will not connect
Close all related processes and restart:
```powershell
Get-Process -Name python,Deepchart,Volumetrica* -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## Credits

This project is for educational purposes only. Use with your own accounts.

Rithmic 14-day free trial: https://rithmic.com


deep chart : Not the latest version (STILL HAS ALL MAJOR INDICATORS/FEATURES!)

Lemme explain;
basically the `bridge_mitm_proxy.py` file connects the data feed (makes your demo AMP / CQG guys) think this is the real version.

this file: `vol_hist_server.py` : fools deepcharts into thinking its actually connecting to its own server ( TO GET HISTORICAL DATA)

This file: `ipc_mitm.py` : ion even know bro i got ai to fix an error and it used this. I'm pretty sure i dont even run this while using deep charts.

This file `run_patched_deepchart.ps1` runs deepcharts and the bridge (data feed connector)


Now to connect to the data feed and make demo amp/cqg think its the real version we first need to intercept the connection.

We do this by adding that IP into our hosts file. (you can search more abt this if you want.)
Basically when we do that we can intercept the connection. Keep in mind if you use AMP/CQG on MW or QT, 
then it won't work. But ofc im a geeky mf I make mw studies and QT indicators, so i made this script which removes it from the hosts file. 

# Only rerun this file if you need to use Motivewave or quanttower using AMP/CQG demo accounts. (when you want to use deepcharts with amp cqg run this file again)
`toggle-proxy-hosts.bat` RUN THIS AS ADMIN. It will remove those IPs and allow you to use your other software *AS usual*.



`start_servers.ps1` - this basically runs the `bridge_mitm_proxy.py`, `vol_hist_server.py`, and `run_patched_deepchart.ps1` all 3 processes required to use deepcharts!
Run this file as ADMIN!

`fix_hosts.bat` - crutial file it basically adds the IPs we need to the HOSTS file.
# RUN THIS FILE (abv) 1 time at the start!! This will setup the inital hosts file.


Okay step by step now my didlers:
1. Install python 3.14 (ideally)
2. Open powershell in the directory of wherever you've placed this entire FOLDER!
3. run `pip install -r requirements.txt` this will setup all the python requirements you need. so your bridge and vol servers will actually work LMFAO.
4. Right click `fix_hosts.bat` and run as admin. 
5. in the same command propmt where you did `pip install` type `start_servers.ps1`. This should get your deepcharts to run.
6. Go to connenctions, add a new one. From data feed select CQG, turn on `use demo credentials`. Enter your AMP CQG demo acc details.
<img width="958" height="972" alt="image" src="https://github.com/user-attachments/assets/0d7e129b-4c0b-455a-b03c-61f661532b9d" />

7. (6 7 nah jk your done)

## NOTE: WHENEVER YOU WANT TO USE MW OR QT WITH AMP/CQG DEMO CREDITNALS YOU HAVE TO RUN `toggle-proxy-hosts.bat` AS ADMIN!
### THIS WILL UNDO THE HOST FILE CHANGES!
### WHEN U WANT TO RUN DEEEPCHARTS AGAIN, RUN THE SAME FILE (`toggle-proxy-hosts.bat`) AS ADMIN AGAIN







# Deepchart CQG Proxy Toolkit

This tool lets you use **Deepchart** (a charting program) with **CQG** (a data provider).
It runs a "man-in-the-middle" proxy that sits between Deepchart and CQG so you can
inspect and modify the data flowing between them.

---

## What You Need

- **A Windows computer** (Deepchart only runs on Windows)
- **Python 3.10 or newer** installed (see below)
- **CQG trading account** (username + password from your broker)
- **Deepchart** already installed
- **Administrator access** on your computer (to run the proxy)

---

## Step 1 — Install Python (if you don't have it)

1. Go to https://www.python.org/downloads/
2. Download the latest **Python 3** version
3. Run the installer
4. **IMPORTANT**: Check the box that says **"Add Python to PATH"** before clicking Install
5. Click Install and wait for it to finish

To verify it worked, open **PowerShell** (press `Win + X` and choose "Terminal (Admin)")
and type:

```
python --version
```

You should see something like `Python 3.12.x`.

---

## Step 2 — Download These Files

Place all the files from this project into a folder on your computer, for example:
`C:\Users\YourName\deepchart-proxy`

---

## Step 3 — Install the Required Packages

Open **PowerShell as Administrator** (right-click Start → "Terminal (Admin)").

Navigate to your folder:

```
cd C:\Users\YourName\deepchart-proxy
```

Then run:

```
pip install -r requirements.txt
```

Wait for it to finish — it installs the tools this proxy needs.

---

## Step 4 — Redirect CQG to Your Computer

This step tells Windows to send CQG traffic to your computer instead of the real CQG
servers, so the proxy can intercept it.

### Easy Way (Recommended)

Double-click **`fix_hosts.bat`** and **Run as Administrator** (right-click it →
"Run as administrator"). It will:
1. Auto-detect your computer's local IP
2. Ask you to confirm it's correct
3. Add the needed entries to your hosts file

### Manual Way (If the script doesn't work)

1. Open **Notepad as Administrator** (right-click Notepad → "Run as administrator")
2. Go to **File → Open** and paste this path:
   ```
   C:\Windows\System32\drivers\etc\hosts
   ```
   (You may need to change the file filter from "Text Documents" to "All Files")
3. **Find your computer's local IP address**:
   - Open a new PowerShell window and type: `ipconfig`
   - Look for the line that says `IPv4 Address` — it will look like `192.168.x.x`
   - Write that number down
4. Add these lines at the **bottom** of the hosts file (replace `192.168.x.x` with
   your actual IP from step 3):

```
192.168.x.x  demoapi.cqg.com
192.168.x.x  api.cqg.com
192.168.x.x  depth-it.historical.deepcharts.com
192.168.x.x  data-b.historical.deepcharts.com
```

5. Save the file and close Notepad

**What this does**: When Deepchart tries to reach `demoapi.cqg.com`, Windows will
send the traffic to your computer instead, where the proxy is waiting.

> ⚠️ **If your computer restarts or changes networks**, your IP might change.
> You'll need to update the hosts file with the new IP (re-run `fix_hosts.bat`).

---

## Step 5 — Install the Security Certificate (One-Time)

The proxy creates its own security certificate so it can decrypt CQG's traffic.
You need to tell Windows to trust it.

1. Open your folder (`C:\Users\YourName\deepchart-proxy`)
2. Open the folder called `mitm_ca`
3. **Right-click** the file `ca.pem` → **Install Certificate**
4. Choose **Local Machine** → click Next
5. Choose **Place all certificates in the following store** → click Browse
6. Select **Trusted Root Certification Authorities** → OK → Next → Finish
7. Click Yes if Windows asks for confirmation

**Don't see `mitm_ca` folder?** Run the proxy first (Step 6), it will create the
folder and certificates automatically. Then come back to this step.

---

## Step 6 — Run the Proxy (3 Terminals)

You need **three separate PowerShell windows**, all **running as Administrator**.

### Terminal 1 — The CQG Proxy (stays running)

```powershell
cd C:\Users\YourName\deepchart-proxy
python bridge_mitm_proxy.py
```

Leave this window open. It will show you messages about what it's doing.

### Terminal 2 — The Historical Data Server (stays running)

Open another PowerShell (Admin), then:

```powershell
cd C:\Users\YourName\deepchart-proxy
python vol_hist_server.py
```

Leave this window open too. It handles historical chart data requests.

### Terminal 3 — Launch Deepchart

```powershell
cd C:\Users\YourName\deepchart-proxy
.\run_patched_deepchart.ps1
```

This launches the patched version of Deepchart. Log in with your CQG username
and password.

---

## Step 7 — You're Done!

If everything worked:
- Deepchart should connect and show live data
- Terminal 1 will show the data flowing between Deepchart and CQG
- Terminal 2 will respond to historical data requests

---

## Troubleshooting

### "Permission denied" or "Can't bind to port 443"

You didn't run PowerShell **as Administrator**. Close and reopen it as Admin.

### "Python is not recognized"

You didn't check "Add Python to PATH" during installation. Reinstall Python and
make sure to check that box.

### "No module named..."

You forgot to run `pip install -r requirements.txt`. Run that command from your
project folder.

### Deepchart connects but no data shows

Your hosts file might have the wrong IP address. Run `ipconfig` again to check
your current IP, then update the hosts file.

### The proxy starts but Deepchart won't connect

Try closing everything and starting fresh:

```powershell
# In any Admin PowerShell:
Get-Process -Name python,Deepchart,Volumetrica* -ErrorAction SilentlyContinue | Stop-Process -Force
```

Then start the three terminals again in order.

---

## What Each File Does

| File | What it's for |
|------|--------------|
| `bridge_mitm_proxy.py` | The main proxy — sits between Deepchart and CQG |
| `vol_hist_server.py` | Handles historical chart data (so charts don't hang) |
| `ipc_mitm.py` | (Optional) Monitors communication between Deepchart and its bridge |
| `run_patched_deepchart.ps1` | Launches Deepchart with required patches |
| `mitm_ca/` | Folder with security certificates (auto-created) |
| `cqg_test/` | Helper files the proxy uses to understand CQG's data format |
| `logs/` | Folder where log files are saved (auto-created) |
| `requirements.txt` | List of packages to install (Step 3) |

---

## Credits

This is for **educational purposes only**. Use with your own CQG account.

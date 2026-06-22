# Issues Tracker

## Fixed

1. **start_servers.ps1 — Python executable not found** — When `RITHMIC_MODE` is set, the script pointed to a hardcoded path (`C:\Users\erand.bazaj\...\Python313`) that doesn't exist on this machine. Fixed by pointing to `.venv311\Scripts\python.exe`.

2. **protobuf 4.x incompatible with Python 3.14** — `async_rithmic` requires `protobuf<5`, which uses C extensions with custom `tp_new` metaclasses removed in Python 3.14. Fixed by creating a Python 3.11.15 venv (`.venv311`) with all dependencies installed.

3. **bridge_mitm_proxy.py crashes with NameError on `ServerMsg`** — `log_server_msg_parsed(msg: ServerMsg)` at line 732 uses `ServerMsg` as a type hint at module level, but it only exists when CQG protobufs are found. Symlinked `cqg_test/` from `C:\Users\illnoobis\Documents\Deepcharts\cqg_test` into the project root.

4. **CQG protobufs not found** — The `cqg_test/` directory was missing from the project. Created a symlink to `C:\Users\illnoobis\Documents\Deepcharts\cqg_test`.

5. **Port 443 in use by `svchost/Appinfo` (IP Helper)** — Requires Administrator privileges to free. Script now detects this and reports it.

6. **SSL certificate verification failure when connecting to Rithmic** — `async_rithmic` rejects the MITM proxy's self-signed cert when hosts file redirects Rithmic traffic. Fixed by setting a permissive SSL context (`CERT_NONE`) on the `RithmicClient` in both `rithmic_translator.py` and `rithmic_bridge.py`.

7. **toggle-proxy-hosts.ps1 redirected Rithmic traffic to localhost** — The `rituz00100.rithmic.com` hosts entry caused the Rithmic client to connect to the proxy instead of the real server. Fixed by removing the entry and adding cleanup logic for stale rithmic entries.

8. **README.md contained informal/unclear content** — Rewrote to be professional, focused on Rithmic setup, with clear prerequisites and steps.

## Unfixed / Known Issues

1. **Port 443 requires Administrator** — `start_servers.ps1` cannot bind to port 443 without admin rights because `iphlpsvc` (IP Helper) holds it. Must run as Administrator or run `net stop iphlpsvc` manually.

2. **`rithmic_translator.py` — No transport layer** — `RithmicTranslator` reads CQG messages and produces responses but has no WebSocket/TCP send mechanism. It produces protobuf responses but cannot deliver them to CQG clients.

3. **`rithmic_translator.py` — `consume_tick_queue` is dead code** — The async generator exists but nothing iterates it. Tick data from Rithmic is queued but never forwarded to CQG clients.

4. **`rithmic_translator.py` — `process_tick` doesn't handle `data_type=3` (L2 book)** — Maps `level >= 2` to `data_type=3` in subscribe, but `process_tick` only handles types 1 (last trade) and 2 (BBO). L2 data silently creates malformed quotes.

5. **`rithmic_translator.py` — `_handle_market_data_subscription` returns success on failure** — If `subscribe_to_market_data` throws, it logs a warning but still returns `status_code=0` (success) to the CQG client.

6. **`rithmic_translator.py` — TimeAndSales and TimeBar handlers are stubs** — Return empty success responses with no actual historical data.

7. **`rithmic_translator.py` — Hardcoded ES-specific defaults** — Fallback `tick_size=0.25`, `tick_value=12.50` are ES-specific, not universal across instruments.

8. **`rithmic_translator.py` — No CQG logon credential validation** — Accepts any username/password in logon without authenticating.

9. **`rithmic_bridge.py` — No reconnection logic** — If the Rithmic connection drops, the bridge dies silently with no recovery.

10. **`rithmic_bridge.py` — Race condition on crash** — If `bridge.start()` throws before setting `running = False`, `process_tick_queue` hangs on `get()` indefinitely.

11. **`rithmic_bridge.py` — No auth on WebSocket server** — `TickBroadcaster` accepts any client on `127.0.0.1:8765`. If bound to `0.0.0.0`, this is an info leak.

12. **`_search_exe.py` & `_search_exe2.py` — End-of-file string loss** — The `for byte in data` loop only emits strings on non-printable bytes. If the file ends mid-string, the last string is silently dropped.

13. **`_search_exe.py` & `_search_exe2.py` — Unused `import struct`** — Module imported but never used.

14. **`_search_exe3.py` — Dead no-op code** — Lines checking for `'rithmic'` strings do `pass` (discard everything).

15. **`_search_exe3.py` — `import re` inside loop** — Works but should be at module level.

16. **`_search_exe.py` & `_search_exe2.py` — O(n^2) string concatenation** — `current += bytes([byte])` creates new bytes objects every iteration; slow on large binaries. Files 3 & 4 use faster index-based traversal.

17. **Duplicated Rithmic connection logic** — `rithmic_translator.py` and `rithmic_bridge.py` both implement Rithmic connection/credential handling independently. Should share a common layer.

18. **Global mutable protobuf state** — `_load_protobufs` mutates module-level globals. Multiple instances with different paths silently overwrite each other.

19. **Rithmic `DecodeError: Error parsing message`** — After SSL fix, `async_rithmic` connects to Rithmic but `get_system_info()` fails with protobuf decode error. Possible causes: wrong gateway URL, wrong system name, or credentials issue. Verbose debug logging added to capture raw bytes on failure.

20. **Rithmic intercept proxy needed** — To debug the DecodeError and understand the working protocol, need to capture MotiveWave's Rithmic traffic. `rithmic_intercept_proxy.py` created but not yet tested.

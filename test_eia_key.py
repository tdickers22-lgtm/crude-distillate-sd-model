"""Standalone check of the EIA API key AND all 22 series IDs (incl. the 7
extension IDs flagged VERIFY LOCALLY). Run: python3 test_eia_key.py
Reads EIA_API_KEY from .env in the current folder (same as the notebook).

Prints one line per series; any FAIL names the exact full v1 identifier to fix.
The notebook's fetch layer treats the 11 core series as required and the 7
extension series (PADD + prices) as skip-with-warning."""
import os
from pathlib import Path
import requests

if Path(".env").exists():
    for line in Path(".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

key = os.environ.get("EIA_API_KEY")
if not key:
    raise SystemExit("No EIA_API_KEY found -- check your .env file is in this folder.")

CORE = ["WCRFPUS2", "WCEIMUS2", "WCREXUS2", "WCRRIUS2", "WCESTUS1",
        "W_EPC0_SAX_YCUOK_MBBL",
        "WDIRPUS2", "WDIIMUS2", "WDIEXUS2", "WDIUPUS2", "WDISTUS1"]
EXT = ["WDISTP11", "WDISTP21", "WDISTP31", "WDISTP41", "WDISTP51",   # PADD stocks (Mb)
       "RWTC",                                                       # WTI spot ($/bbl)
       "EER_EPD2DXL0_PF4_Y35NY_DPG",                                 # NYH ULSD ($/gal)
       "RCLC1", "RCLC2",                                             # WTI futures M1/M2 ($/bbl)
       "EER_EPD2F_PE1_Y35NY_DPG", "EER_EPD2F_PE2_Y35NY_DPG"]         # HO futures M1/M2 ($/gal)

fails = []
for sid in CORE + EXT:
    # the seriesid compatibility route needs the FULL v1 id: PET.<code>.W
    full_id = f"PET.{sid}.W"
    tag = "core" if sid in CORE else "EXT "
    try:
        r = requests.get(f"https://api.eia.gov/v2/seriesid/{full_id}",
                         params={"api_key": key, "length": 2}, timeout=30)
        if r.status_code == 200:
            rows = r.json()["response"]["data"]
            if not rows:   # HTTP 200 with zero rows is NOT a verified series
                fails.append(full_id)
                print(f"  FAIL [{tag}] {full_id:<38} returned 0 rows (valid route, empty series?)")
                continue
            latest = rows[0]
            print(f"  OK   [{tag}] {full_id:<38} latest {latest.get('period')}: "
                  f"{latest.get('value')} {latest.get('units', '')}")
        else:
            fails.append(full_id)
            print(f"  FAIL [{tag}] {full_id:<38} HTTP {r.status_code}: {r.text[:120]}")
    except Exception as e:
        fails.append(full_id)
        print(f"  FAIL [{tag}] {full_id:<38} {e}")

print()
if fails:
    print(f"{len(fails)} series failed -- fix these IDs (candidates/fallbacks in DECISIONS.md #13-14):")
    for f in fails:
        print("  ", f)
else:
    print("All 22 series verified. Run the notebook to refresh the live cache.")

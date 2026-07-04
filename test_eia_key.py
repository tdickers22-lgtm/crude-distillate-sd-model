"""Quick standalone test of the EIA API fix. Run: python3 test_eia_key.py
Reads EIA_API_KEY from .env in the current folder (same as the notebook)."""
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

url = "https://api.eia.gov/v2/seriesid/PET.WCESTUS1.W"  # commercial crude stocks, weekly
r = requests.get(url, params={"api_key": key, "length": 3}, timeout=30)
print("HTTP status:", r.status_code)
print("URL called: ", r.url.replace(key, "***KEY***"))

if r.status_code == 200:
    data = r.json()["response"]["data"]
    print("\nSuccess! Latest crude stock readings (Mb):")
    for row in data:
        print(f"  {row['period']}: {row['value']}")
else:
    print("\nFailed. Response body:")
    print(r.text[:500])

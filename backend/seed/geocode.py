"""Fill in latitude/longitude in seed/data/services.csv using OpenStreetMap Nominatim (US-01).

Owner: Dhara.
Run once after adding services:  python -m seed.geocode   (from the backend folder)

Only rows with an empty latitude or longitude are looked up, so running it again
doesn't call Nominatim for addresses that are already done. The seed script never
geocodes; it just reads the saved coordinates.

Nominatim usage policy: at most 1 request per second and a User-Agent that names the app.
https://operations.osmfoundation.org/policies/nominatim/
"""

import csv
import json
import re
import time
import urllib.parse
import urllib.request

from seed.seed import DATA_FILE

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "ThunderLink/0.1 (COMP 3415 student project, Lakehead University)"

# Rough box around the city of Thunder Bay. Results outside it are treated as wrong matches.
THUNDER_BAY_BOUNDS = {"south": 48.30, "north": 48.55, "west": -89.45, "east": -89.10}


def street_part(address: str) -> str:
    """'86 Cumberland St S, Thunder Bay, ON P7B 2V3' -> '86 Cumberland St S'."""
    return address.split(",")[0].strip()


def postal_code(address: str) -> str | None:
    match = re.search(r"[A-Z]\d[A-Z] ?\d[A-Z]\d", address)
    return match.group(0) if match else None


def in_thunder_bay(lat: float, lng: float) -> bool:
    b = THUNDER_BAY_BOUNDS
    return b["south"] <= lat <= b["north"] and b["west"] <= lng <= b["east"]


def lookup(params: dict) -> tuple[float, float] | None:
    query = urllib.parse.urlencode({**params, "format": "json", "limit": 1, "countrycodes": "ca"})
    request = urllib.request.Request(f"{NOMINATIM_URL}?{query}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        results = json.load(response)
    time.sleep(1.1)  # stay under 1 request per second
    if not results:
        return None
    lat, lng = float(results[0]["lat"]), float(results[0]["lon"])
    return (lat, lng) if in_thunder_bay(lat, lng) else None


def geocode(address: str) -> tuple[float, float] | None:
    """Try the street address first, then the postal code (accurate to a few blocks)."""
    street = street_part(address)
    found = lookup({"street": street, "city": "Thunder Bay", "state": "Ontario", "country": "Canada"})
    if found is None:
        # Nominatim sometimes misses the direction suffix, e.g. "Cumberland St S".
        short = re.sub(r"\s+[NSEW]$", "", street)
        if short != street:
            found = lookup({"street": short, "city": "Thunder Bay", "state": "Ontario", "country": "Canada"})
    if found is None and (code := postal_code(address)):
        found = lookup({"postalcode": code, "city": "Thunder Bay", "country": "Canada"})
    return found


def run() -> None:
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    missing = []
    for row in rows:
        if row["latitude"] and row["longitude"]:
            continue
        coords = geocode(row["address"])
        if coords is None:
            missing.append(row["name"])
            print(f"NOT FOUND  {row['name']}  ({row['address']})")
            continue
        row["latitude"], row["longitude"] = f"{coords[0]:.6f}", f"{coords[1]:.6f}"
        print(f"ok         {row['name']}  {row['latitude']}, {row['longitude']}")

    with DATA_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    if missing:
        print(f"\n{len(missing)} address(es) need coordinates added by hand.")


if __name__ == "__main__":
    run()

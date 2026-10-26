"""Checks on seed/data/services.csv (US-01). Owner: Dhara.

These run against the CSV file itself, so a bad row is caught before the seed script loads it.
"""

import csv

import pytest

from seed.geocode import in_thunder_bay
from seed.seed import DATA_FILE

REQUIRED = ["name", "category", "address", "latitude", "longitude"]


@pytest.fixture(scope="module")
def rows():
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_csv_has_the_columns_the_seed_script_expects():
    with DATA_FILE.open(newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == [
        "name", "category", "description", "address", "latitude", "longitude",
        "hours", "phone", "website", "eligibility",
    ]


def test_csv_has_at_least_50_services(rows):
    assert len(rows) >= 50


@pytest.mark.parametrize("field", REQUIRED)
def test_every_service_has_required_field(rows, field):
    missing = [row["name"] for row in rows if not row[field].strip()]
    assert missing == []


def test_every_service_is_geocoded_inside_thunder_bay(rows):
    outside = [
        row["name"] for row in rows
        if not in_thunder_bay(float(row["latitude"]), float(row["longitude"]))
    ]
    assert outside == []


def test_no_duplicate_name_and_address(rows):
    keys = [(row["name"], row["address"]) for row in rows]
    assert len(keys) == len(set(keys))


def test_websites_are_full_urls(rows):
    bad = [row["name"] for row in rows if row["website"] and not row["website"].startswith("https://")]
    assert bad == []

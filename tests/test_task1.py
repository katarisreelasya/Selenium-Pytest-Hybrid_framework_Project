import os
import time
import csv
import pytest
from pages.task1_page import Task1Page

# Project ROOT = parent of "tests" folder
ROOT = os.path.dirname(os.path.dirname(__file__))

# The EXACT file created by Task1Page
CSV_FILE = os.path.join(ROOT, "outputs", "upcoming_honda_bikes.csv")


def wait_for_csv(path: str, timeout: int = 30) -> bool:
    """Wait until CSV appears and is not empty."""
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return True
        time.sleep(0.5)
    return False


@pytest.mark.task1
def test_task1(driver):
    page = Task1Page(driver)
    page.run()

    # Validate CSV existence
    assert wait_for_csv(CSV_FILE, timeout=30), f"CSV not found or empty: {CSV_FILE}"
    assert os.path.isfile(CSV_FILE), f"Not a file: {CSV_FILE}"
    assert os.path.getsize(CSV_FILE) > 0, "CSV exists but is empty"

    # Validate rows inside the CSV
    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    # Must have header + at least one data row
    assert len(rows) >= 2, "CSV must contain headers + at least one data row"

    headers = rows[0]
    assert all(h.strip() for h in headers), f"Header row invalid or empty: {headers}"

    data_rows = rows[1:]
    assert any(any(cell.strip() for cell in r) for r in data_rows), \
        "CSV contains headers but no actual data rows"

    print("✓ Task‑1 CSV validation passed successfully!")

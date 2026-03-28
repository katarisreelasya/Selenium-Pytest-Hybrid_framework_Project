
import os
import pytest
from pages.task3_page import Task3Page

@pytest.mark.task3
def test_task3(driver):
    # Run your existing functionality using the shared driver
    Task3Page(driver).run()

    # Resolve screenshots folder relative to the project root (parent of tests)
    ROOT = os.path.dirname(os.path.dirname(__file__))
    folder = os.path.join(ROOT, "screenshots")

    assert os.path.isdir(folder), f"'screenshots' folder not found at: {folder}"

    # Get list of .png files
    files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    assert files, "No screenshot found in screenshots folder."

    # Pick the latest file by modification time (more reliable than list order)
    latest = max((os.path.join(folder, f) for f in files), key=os.path.getmtime)

    # Check file is not empty
    assert os.path.getsize(latest) > 0, "Screenshot file is empty."

    print(f"✓ Screenshot captured successfully: {latest}")

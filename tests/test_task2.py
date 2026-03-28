
import pytest
from pages.task2_page import Task2Page

@pytest.mark.task2
def test_task2_print_and_validate(driver, capsys):
    # 1) Run your existing Task‑2 flow (prints the list of popular models)
    page = Task2Page(driver)
    page.run()

    # 2) Capture printed output from Task2Page.run()
    output = capsys.readouterr().out.strip()

    # 3) Re-print same names in test console (for reporting)
    print("\n=== Popular Models (from label list) ===")
    print(output)
    print("Task2 is completed successfully")

    # 4) Simple validations (NO change to logic)
    assert output, "No output was printed by Task2Page().run()"
    assert "." in output, "Expected at least one numbered item like '01. ModelName'"
    assert "\n" in output, "Expected multiple lines of model names"

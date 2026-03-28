# pages/task2_page.py

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.helpers import close_overlays

class Task2Page:

    def __init__(self, driver):
        self.driver = driver

    def run(self):
        # Open a new tab and switch to it (as in original flow)
        self.driver.execute_script("window.open('','_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Open site & close overlays
        self.driver.get("https://www.zigwheels.com/")
        close_overlays(self.driver)
        time.sleep(2)

        # Hover over the More element to display submenu (absolute XPath preserved)
        more_element = self.driver.find_element(By.XPATH, "/html/body/header/div[1]/div/div[2]/nav/ul/li[5]/span[1]")
        actions = ActionChains(self.driver)
        actions.move_to_element(more_element).perform()
        time.sleep(2)

        # Click on Used Cars (2nd element) — absolute XPath preserved
        used_cars_element = self.driver.find_element(By.XPATH, "/html/body/header/div[1]/div/div[2]/nav/ul/li[5]/ul/li[2]/a[1]")
        used_cars_element.click()
        time.sleep(3)

        # Find text box and enter 'Chennai' (original selector)
        text_box = self.driver.find_element(By.XPATH, "//*[@id='gs_input5']")
        text_box.send_keys("Chennai")
        time.sleep(2)

        # Pick first suggestion item (absolute XPath preserved)
        pickup_element = self.driver.find_element(By.XPATH, "/html/body/ul[4]/li[1]/a[1]")
        pickup_element.click()

        # === Collect their texts in a list (original label XPaths preserved) ===
        checkbox_xpaths = [
            "//label[@for='bycarid22_317']",
            "//label[@for='bycarid22_338']",
            "//label[@for='bycarid10_146']",
            "//label[@for='bycarid10_156']",
            "//label[@for='bycarid8_125']",
            "//label[@for='bycarid13_207']",
            "//label[@for='bycarid13_205']",
            "//label[@for='bycarid21_314']",
        ]

        popular_models = []
        seen = set()

        # Scroll to the first label area (helps with lazy content/visibility)
        first_label = self.driver.find_element(By.XPATH, checkbox_xpaths[0])
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_label)
        time.sleep(1)

        # Read label texts, keep unique, maintain order
        for xp in checkbox_xpaths:
            try:
                lbl = self.driver.find_element(By.XPATH, xp)
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", lbl)
                time.sleep(0.2)
                text = lbl.text.strip()
                if text and text not in seen:
                    seen.add(text)
                    popular_models.append(text)
                    time.sleep(0.2)
            except Exception as e:
                print(f"Error reading label {xp}: {str(e)}")

        # Final display (exact formatting preserved: numbered with 2 digits)
        print()
        for i, m in enumerate(popular_models, 1):
            print(f"{i:02d}. {m}")

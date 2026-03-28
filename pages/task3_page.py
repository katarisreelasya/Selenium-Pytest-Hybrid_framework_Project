
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.helpers import close_overlays


class Task3Page:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def run(self):
        # Open new tab (same as original task3)
        self.driver.execute_script("window.open('','_blank');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            # -------------------- OPEN SITE --------------------
            self.driver.get("https://www.zigwheels.com/")
            close_overlays(self.driver)
            time.sleep(2)

            # -------------------- CLICK LOGIN ICON --------------------
            login_icon = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='des_lIcon']"))
            )
            login_icon.click()
            time.sleep(2)

            # -------------------- CLICK CONTINUE WITH GOOGLE --------------------
            google_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'googleSignIn')]"))
            )

            # Track tab handles
            main_tab = self.driver.current_window_handle #stores current window id
            old_handles = set(self.driver.window_handles)   #converting all window handles to a set

            google_btn.click()  #Continue with Google

            # Wait until Google popup window appears
            try:
                self.wait.until(lambda d: len(set(d.window_handles) - old_handles) == 1)    #len({"CDwindow-new"} - {"CDwindow-abc"}) == 1
            except TimeoutException:
                raise RuntimeError("Google sign‑in window did not open.")

            new_tab = list(set(self.driver.window_handles) - old_handles)[0]
            self.driver.switch_to.window(new_tab)

            # -------------------- ENTER INVALID EMAIL --------------------
            invalid_email = "no-such-user-987654321@example.com"
            email_box = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, "//input[@id='identifierId']"))
            )
            email_box.clear()
            email_box.send_keys(invalid_email)

            next_btn = self.wait.until(EC.element_to_be_clickable((By.ID, "identifierNext")))
            next_btn.click()

            # -------------------- CAPTURE ERROR MESSAGE --------------------
            error_text = ""
            try:
                # Primary Google error container
                err_el = self.wait.until(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'o6cuMc')]"))
                )
                error_text = err_el.text.strip()

            except Exception:
                try:
                    # Fallback: aria-live assertive
                    err_el = self.wait.until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "//*[@aria-live='assertive' and string-length(normalize-space())>0]")
                        )
                    )
                    error_text = err_el.text.strip()
                except Exception:
                    try:
                        # Fallback: other known Google error containers
                        err_el = self.wait.until(
                            EC.visibility_of_element_located(
                                (By.XPATH,
                                 "//div[contains(@class,'Ee6h0d') or contains(@class,'GQ8Pzc') "
                                 "or contains(@class,'LXRPh')]//*[string-length(normalize-space())>0]")
                            )
                        )
                        error_text = err_el.text.strip()
                    except Exception:
                        error_text = "(Could not locate error text — UI may have changed)"

            print(f"\nGoogle login error message: {error_text}")

            # -------------------- SCREENSHOT --------------------
            os.makedirs("screenshots", exist_ok=True)
            screenshot_path = os.path.join(
                "screenshots", f"google_login_error_{int(time.time())}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            print(f"Saved screenshot: {screenshot_path}")

            # -------------------- CLOSE POPUP & RETURN --------------------
            try:
                if self.driver.current_window_handle != main_tab:
                    self.driver.close()  # Close Google popup
                    self.driver.switch_to.window(main_tab)
            except Exception:
                pass

        except Exception as e:
            print(f"Task‑3 encountered an error: {e}")

            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
            except Exception:
                pass


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time, csv, os

from utils.helpers import (
    close_overlays, smooth_scroll_by, smooth_scroll_into_view_center,
    pulse_highlight, element_is_at_click_point,
    find_brand_section, find_arrow, find_horizontal_container,
    js_scroll_horizontally, locate_honda_img,
    clean_text, ensure_dir, SCROLL_PAUSE, HOVER_PAUSE, CLICK_PAUSE
)
class Task1Page:

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def run(self):

        # ------------------ STEP 1: Open site ------------------
        self.driver.get("https://www.zigwheels.com/")
        close_overlays(self.driver)

        NEW_BIKES_XP = "//span[normalize-space()='NEW BIKES']"
        UPCOMING_BIKES_XP = "//a[contains(@data-track-label,'nav-upcoming-bikes')]"

        new_bikes = self.wait.until(
            EC.visibility_of_element_located((By.XPATH, NEW_BIKES_XP))
        )
        ActionChains(self.driver).move_to_element(new_bikes).pause(HOVER_PAUSE).perform()

        upcoming_bikes = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, UPCOMING_BIKES_XP))
        )
        ActionChains(self.driver).move_to_element(upcoming_bikes).pause(HOVER_PAUSE).click().perform()

        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[self::h1 or self::h2][contains(translate(.,'UPCOMING','upcoming'),'upcoming')]")
        ))
        time.sleep(CLICK_PAUSE)

        # ---------------- STEP 2: Click Upcoming Bikes Under 5 Lakh ----------------
        UNDER5_XP = "//a[contains(normalize-space(.), 'Upcoming Bikes Under 5 Lakh')]"
        link = None
        for _ in range(45):
            try:
                link = self.driver.find_element(By.XPATH, UNDER5_XP)
                break
            except:
                smooth_scroll_by(self.driver, 300)

        if not link:
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(SCROLL_PAUSE)
            try:
                link = self.driver.find_element(By.XPATH, UNDER5_XP)
            except:
                pass

        if link:
            smooth_scroll_into_view_center(self.driver, link)
            pulse_highlight(self.driver, link, cycles=2)
            time.sleep(HOVER_PAUSE)
            try:
                self.wait.until(EC.element_to_be_clickable((By.XPATH, UNDER5_XP))).click()
            except:
                self.driver.execute_script("window.scrollBy(0, -120);")
                link.click()
            time.sleep(CLICK_PAUSE)
        else:
            print("Could not find 'Upcoming Bikes Under 5 Lakh(s)' link.")

        # ---------------- STEP 3: Find Honda Image in Brand Carousel ----------------
        section = find_brand_section(self.driver) #helper to find the section containing brand carousel, if exists. If not found, returns None

        if section is None:
            print("Brand carousel not found. Opening manufacturers page...")
            self.driver.get("https://www.zigwheels.com/newbikes/manufacturers")
            close_overlays(self.driver)
            section = find_brand_section(self.driver)
            if section is None:
                section = self.driver.find_element(By.XPATH, "//body")

        honda_img = locate_honda_img(section)
        max_clicks = 12
        
        if honda_img is None:
            for _ in range(max_clicks):
                right = find_arrow(self.driver, section, "right")
                if right:
                    right.click()
                    time.sleep(SCROLL_PAUSE)
                else:
                    viewport = find_horizontal_container(section)
                    if not viewport:
                        break
                    js_scroll_horizontally(self.driver, viewport, +320)

                honda_img = locate_honda_img(section)
                if honda_img:
                    break

        if honda_img is None:
            for _ in range(max_clicks):
                left = find_arrow(self.driver, section, "left")
                if left:
                    left.click()
                    time.sleep(SCROLL_PAUSE)
                else:
                    viewport = find_horizontal_container(section)
                    if not viewport:
                        break
                    js_scroll_horizontally(self.driver, viewport, -320)

                honda_img = locate_honda_img(section)
                if honda_img:
                    break

        if honda_img:
            smooth_scroll_into_view_center(self.driver, honda_img)
            smooth_scroll_by(self.driver, -220)
            ActionChains(self.driver).move_to_element(honda_img).pause(HOVER_PAUSE).perform()
            pulse_highlight(self.driver, honda_img, cycles=2)
            time.sleep(CLICK_PAUSE)

            try:
                if not element_is_at_click_point(self.driver, honda_img):
                    self.driver.execute_script("window.scrollBy(0, -120);")
                    time.sleep(SCROLL_PAUSE)
                honda_img.click()
            except:
                try:
                    honda_img.find_element(By.XPATH, "./ancestor::a[1]").click()
                except:
                    self.driver.execute_script("arguments[0].click();", honda_img)
            time.sleep(CLICK_PAUSE)

        else:
            print("Honda tile not found. Continuing...")

        # ---------------- STEP 4: Extract upcoming Honda bike cards ----------------
        try:
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "//*[self::h1 or self::h2][contains(translate(.,'UPCOMING HONDA BIKES','upcoming honda bikes'),'upcoming honda bikes')]")
            ))
        except:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//body")))
            time.sleep(1)

        rows = self.extract_upcoming_cards()
        #If data found: Creates directory, writes CSV with headers and rows.
        if rows:
            print("\nUpcoming Honda Bikes (≤ ₹5 Lakhs) ---")
            ensure_dir("outputs/upcoming_honda_bikes.csv")

            with open("outputs/upcoming_honda_bikes.csv", "w",
                      newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Bike Name", "Price (as shown)", "Expected Launch"])
                w.writerows(rows)

            print(f"\n✔ CSV saved: outputs/upcoming_honda_bikes.csv")
        else:
            print("\nNo upcoming Honda bikes detected.")

    def extract_upcoming_cards(self):
        rows = []

        cards = self.driver.find_elements(By.XPATH, "//li[contains(@class,'modelItem')]")
        if not cards:
            cards = self.driver.find_elements(By.XPATH,
                "//li | //div[contains(@class,'modelItem') or contains(@class,'upcoming')]"
            )
        if not cards:
            return rows

        for card in cards:
            # name
            name = ""
            for xp in [".//h3", ".//h2", ".//a[contains(@href,'bike')][1]"]:
                try:
                    name = clean_text(card.find_element(By.XPATH, xp).text)
                    if name:
                        break
                except:
                    pass

            # price
            price = ""
            for xp in [
                ".//*[contains(.,'Lakh') or contains(.,'₹') or contains(.,'Rs')][1]",
                ".//span[contains(.,'Lakh') or contains(.,'₹') or contains(.,'Rs')][1]",
            ]:
                try:
                    price = clean_text(card.find_element(By.XPATH, xp).text)
                    if price:
                        break
                except:
                    pass

            # launch
            launch = ""
            for xp in [
                ".//*[contains(translate(.,'LAUNCH','launch'),'launch')][1]",
                ".//*[contains(.,'Expected') and contains(.,'Launch')][1]",
            ]:
                try:
                    launch = clean_text(card.find_element(By.XPATH, xp).text)
                    if launch:
                        break
                except:
                    pass
            # Append to rows if we have at least a name. Price and launch can be empty.
            if name:
                rows.append([name, price, launch])

        return rows
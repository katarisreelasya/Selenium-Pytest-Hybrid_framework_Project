import time, os, re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ===== SPEED SETTINGS (same as original) =====
SPEED = "slow"  # "slow" | "normal" | "fast"
SCROLL_STEP = {"slow": 200, "normal": 400, "fast": 700}[SPEED]
SCROLL_PAUSE = {"slow": 0.35, "normal": 0.20, "fast": 0.10}[SPEED]
HOVER_PAUSE = {"slow": 0.90, "normal": 0.45, "fast": 0.20}[SPEED]
CLICK_PAUSE = {"slow": 1.10, "normal": 0.55, "fast": 0.25}[SPEED]


# ========== DIRECTORY CREATOR ==========
def ensure_dir(path):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


# ========== COOKIE POPUP CLOSER ==========
def close_overlays(driver):
    for xp in [
        "//button[normalize-space()='Accept']",
        "//button[contains(.,'Accept')]",
        "//button[contains(.,'OK')]",
        "//button[contains(.,'Got it')]",
    ]:
        try:
            driver.find_element(By.XPATH, xp).click()
            time.sleep(0.2)
            break
        except Exception:
            pass


# ========== SCROLLING + HIGHLIGHT FX ==========
def smooth_scroll_by(driver, pixels, step=SCROLL_STEP, pause=SCROLL_PAUSE):
    direction = 1 if pixels >= 0 else -1
    pixels = abs(pixels)
    moved = 0
    while moved < pixels:
        chunk = min(step, pixels - moved)
        driver.execute_script(f"window.scrollBy(0, {direction * chunk})")
        moved += chunk
        time.sleep(pause)


def smooth_scroll_into_view_center(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({behavior:'smooth', block:'center'});", el)
    time.sleep(max(SCROLL_PAUSE, 0.35))
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, -70);")
        time.sleep(SCROLL_PAUSE)


def pulse_highlight(driver, el, cycles=2):
    try:
        orig = driver.execute_script("return arguments[0].getAttribute('style') || '';", el)
        for _ in range(cycles):
            driver.execute_script(
                "arguments[0].setAttribute('style', arguments[0].getAttribute('style') + "
                "'outline: 4px solid yellow; outline-offset: 3px; transition: outline .15s ease;');", el)
            time.sleep(0.4 if SPEED == "slow" else 0.25)

            driver.execute_script(
                "arguments[0].setAttribute('style', arguments[0].getAttribute('style') + "
                "'outline: 4px solid #ff4747; outline-offset: 3px; transition: outline .15s ease;');", el)
            time.sleep(0.4 if SPEED == "slow" else 0.25)

        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", el, orig)
    except Exception:
        pass


def element_is_at_click_point(driver, el):
    return driver.execute_script("""
        const el = arguments[0];
        const r = el.getBoundingClientRect();
        const cx = Math.floor(r.left + r.width/2);
        const cy = Math.floor(r.top + r.height/2);
        const topEl = document.elementFromPoint(cx, cy);
        return (el === topEl) || el.contains(topEl);
    """, el)


# ========== CAROUSEL HELPERS ==========
def find_brand_section(driver):
    for hdr_xp in [
        "//h2[contains(.,'Top New Bike Brands in India')]/ancestor::*[self::section or self::div][1]",
        "//h2[contains(.,'Search Bikes by Top Brands')]/ancestor::*[self::section or self::div][1]",
        "//h2[contains(.,'Upcoming Bikes by Brand')]/ancestor::*[self::section or self::div][1]",
    ]:
        try:
            sec = driver.find_element(By.XPATH, hdr_xp)
            smooth_scroll_into_view_center(driver, sec)
            return sec
        except NoSuchElementException:
            smooth_scroll_by(driver, 350)
    return None


def find_arrow(driver, section, direction="right"):
    if direction == "right":
        candidates = [
            ".//button[contains(@class,'slick-next')]",
            ".//div[contains(@class,'slick-next')]",
            ".//button[contains(@aria-label,'Next')]",
            ".//span[contains(@class,'next')]/ancestor::button[1]",
        ]
    else:
        candidates = [
            ".//button[contains(@class,'slick-prev')]",
            ".//div[contains(@class,'slick-prev')]",
            ".//button[contains(@aria-label,'Previous') or contains(@aria-label,'Prev')]",
            ".//span[contains(@class,'prev')]/ancestor::button[1]",
        ]

    for xp in candidates:
        try:
            return section.find_element(By.XPATH, xp)
        except NoSuchElementException:
            pass

    for xp in [xp.replace(".//", "//") for xp in candidates]:
        try:
            return driver.find_element(By.XPATH, xp)
        except NoSuchElementException:
            pass

    return None


def find_horizontal_container(section):
    for xp in [
        ".//*[contains(@class,'slick-track')]/..",
        ".//*[contains(@class,'slick-list')]",
        ".//*[contains(@class,'brand') and (self::div or self::ul)]",
        ".//ul",
    ]:
        try:
            return section.find_element(By.XPATH, xp)
        except NoSuchElementException:
            continue
    return None


def js_scroll_horizontally(driver, viewport, px):
    driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollLeft + arguments[1];",
                          viewport, px)
    time.sleep(SCROLL_PAUSE)


def locate_honda_img(section):
    for xp in [
        ".//a[@title='Honda Bikes']//img",
        ".//a[@title='Honda']//img",
        ".//img[contains(@alt,'Honda')]",
        ".//a[contains(@href,'honda')][.//img]//img",
    ]:
        try:
            return section.find_element(By.XPATH, xp)
        except NoSuchElementException:
            pass
    return None


# ========== CARD EXTRACTION ==========
def clean_text(s: str):
    return re.sub(r"\s+", " ", (s or "").strip())
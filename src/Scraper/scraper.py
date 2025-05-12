import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import get_nearest_city, extract_prices

logger = logging.getLogger(__name__)

def configure_driver():
    options = Options()
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    logger.info("Web driver configured for headless operation.")
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Web driver successfully initialized.")
        return driver
    except WebDriverException as e:
        logger.error(f"Web driver initialization failed: {e}")
        raise

def wait_for_element(driver, by, value, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        logger.error(f"Element {value} not found after waiting for {timeout} seconds.")
        return None

def update_names_for_urls(updated_data):
    logger.info("Starting update_names_for_urls function.")
    driver = configure_driver()
    updated_data_with_names = {}

    for url_index, (url, data) in enumerate(updated_data.items()):
        logger.info(f"[{url_index+1}/{len(updated_data)}] Processing URL: {url}")
        try:
            driver.get(url)
            parts = url.split("/")
            region_name = parts[4]
        except Exception as e:
            logger.error(f"Failed to load URL {url}: {e}")
            continue

        # Use waits for elements instead of direct access to avoid race conditions
        administrative_area_element = wait_for_element(driver, By.ID, "address")
        administrative_area = administrative_area_element.text.split(',')[0].split('\n')[-1].strip() if administrative_area_element else ""

        campground_name_element = wait_for_element(driver, By.CSS_SELECTOR, "h1")
        campground_name = campground_name_element.text if campground_name_element else ""

        type_name_element = wait_for_element(driver, By.CLASS_NAME, "CampgroundDetails_header__title-label__B27_R")
        type_name = type_name_element.text if type_name_element else ""

        coordinates_element = wait_for_element(driver, By.ID, "coordinates")
        coordinates = coordinates_element.text.split() if coordinates_element else ["", "", ""]

        nearest_info_element = wait_for_element(driver, By.CLASS_NAME, "DriveTimeWidget_drive-time__links__WwTS5")
        nearest_city = get_nearest_city(nearest_info_element.text)[0] if nearest_info_element else ""

        accommodation_type_names_element = wait_for_element(driver, By.CLASS_NAME, "CampgroundSiteTypes_site-types__category__5J51O")
        accommodation_type_names = [s.strip() for s in accommodation_type_names_element.text.split("\n")] if accommodation_type_names_element else []

        camper_type_elements = driver.find_elements(By.CLASS_NAME, "AppAvatar_avatar__level-title__E3GvH")
        camper_types = list(dict.fromkeys([el.text for el in camper_type_elements]))

        try:
            driver.find_element(By.XPATH, "//*[contains(text(), 'Check Availability')]")
            bookable = True
        except NoSuchElementException:
            bookable = False

        href_element = wait_for_element(driver, By.LINK_TEXT, "Visit Website")
        href = href_element.get_attribute('href') if href_element else "*"

        rating_elements = wait_for_element(driver, By.CLASS_NAME, "CampgroundReviews_ratings__total-container__4RpaO")
        if rating_elements:
            rating, reviews_count = rating_elements.text.split()[0], rating_elements.text.split()[4]
        else:
            rating, reviews_count = 0, 0

        price_element = wait_for_element(driver, By.CLASS_NAME, "CampgroundStickyBar_sticky-bar__price-container__vJ2er")
        price = extract_prices(price_element.text) if price_element else [0, 0]

        slug = parts[-1]

        updated_data_with_names[url] = {
            **data,
            "links": url,
            "name": campground_name,
            "region-name": region_name,
            "administrative_area": administrative_area,
            "latitude": coordinates[0],
            "longitude": coordinates[2],
            "nearest_city_name": nearest_city,
            "type": type_name,
            "accommodation_type_names": accommodation_type_names,
            "camper_types": camper_types,
            "bookable": bookable,
            "operator": href,
            "rating": rating,
            "reviews_count": reviews_count,
            "price_low": price[0],
            "price_high": price[1],
            "slug": slug
        }

        logger.info(f"Data extracted and updated for: {campground_name or slug}")

    driver.quit()
    logger.info("Driver session closed.")
    logger.info("update_names_for_urls function completed.")
    return updated_data_with_names

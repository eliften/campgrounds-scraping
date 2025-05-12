import re
import logging

logger = logging.getLogger(__name__)

def extract_prices(price_text: str) -> list:
    price_pattern = r"\$(\d+(?:\.\d+)?)\s*-\s*\$(\d+(?:\.\d+)?)"
    single_price_pattern = r"\$(\d+(?:\.\d+)?)\s*/\s*night"

    match = re.search(price_pattern, price_text)
    if match:
        price_low = float(match.group(1))
        price_high = float(match.group(2))
        logger.debug(f"Price range extracted: low={price_low}, high={price_high}")
        return [price_low, price_high]

    match = re.search(single_price_pattern, price_text)
    if match:
        price = float(match.group(1))
        logger.debug(f"Single price extracted: {price}")
        return [price, price]

    logger.warning(f"No price found in text: {price_text}")
    return [None, None]


def get_nearest_city(text: str) -> tuple:
    city_distance_with_minutes = []
    matches = re.findall(r"(?:(\d+)\s*hr[s]?\s*)?(?:(\d+)\s*min)?\s*from\s+([a-zA-Z\s]+)", text)
    for hr, min_, city in matches:
        hr = int(hr) if hr else 0
        min_ = int(min_) if min_ else 0
        total_minutes = hr * 60 + min_
        city_distance_with_minutes.append((city.strip(), total_minutes))
        logger.debug(f"Parsed city: {city.strip()}, travel time: {total_minutes} min")

    if city_distance_with_minutes:
        nearest_city = min(city_distance_with_minutes, key=lambda x: x[1])
        logger.info(f"Nearest city identified: {nearest_city[0]} ({nearest_city[1]} min)")
        return nearest_city[0], nearest_city[1]

    logger.warning("No nearest city found.")
    return "Bilinmiyor", None

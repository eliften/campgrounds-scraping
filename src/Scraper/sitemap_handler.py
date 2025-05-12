import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO
import os
import json
import logging

logger = logging.getLogger(__name__)

NAMESPACE = {
    'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    'image': 'http://www.google.com/schemas/sitemap-image/1.1'
}

def load_previous_data(file_path: str) -> dict:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                logger.info(f"Previous data loaded from {file_path}")
                return data
        except Exception as e:
            logger.error(f"Error reading previous data: {e}")
            return {}
    logger.info("No previous data file found.")
    return {}

def download_and_parse_sitemap(url: str) -> ET.Element:
    logger.info(f"Downloading sitemap from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz_file:
            logger.info("Sitemap downloaded and decompressed successfully.")
            return ET.fromstring(gz_file.read())
    logger.error(f"Failed to download sitemap: {response.status_code}")
    raise Exception("Sitemap indirilemedi.")

def get_updated_entries(root: ET.Element, previous_data: dict) -> dict:
    updated = {}
    logger.info("Scanning sitemap for updates...")
    for url_elem in root.findall('ns:url', NAMESPACE):
        loc_elem = url_elem.find('ns:loc', NAMESPACE)
        lastmod_elem = url_elem.find('ns:lastmod', NAMESPACE)

        if loc_elem is None or lastmod_elem is None:
            continue

        loc = loc_elem.text
        lastmod = lastmod_elem.text

        image_locs = url_elem.findall('image:image', NAMESPACE)
        image_urls = [img.find('image:loc', NAMESPACE).text for img in image_locs if img.find('image:loc', NAMESPACE) is not None]

        previous_lastmod = previous_data.get(loc, {}).get("availability_updated_at")
        if previous_lastmod != lastmod:
            logger.debug(f"Updated entry found: {loc}")
            updated[loc] = {
                "availability_updated_at": lastmod,
                "image_count": len(image_urls),
                "photo_url": image_urls[0] if image_urls else None,
                "photo_urls": image_urls
            }
    logger.info(f"Total updated entries: {len(updated)}")
    return updated

def save_data(file_path: str, data: dict):
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            logger.info(f"Data saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving data: {e}")

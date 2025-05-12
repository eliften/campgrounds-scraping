from flask import Flask, jsonify
from pydantic import ValidationError
from src.Scraper.sitemap_handler import download_and_parse_sitemap, get_updated_entries
from src.Scraper.scraper import update_names_for_urls
from src.models.campground import Campground, CampgroundLinks
from src.db.db_methods import insert_campground, load_previous_urls_from_db
import uuid, logging
from typing import Dict
from pydantic import HttpUrl

app = Flask(__name__)

logger = logging.getLogger(__name__)

SITEMAP_URL = "https://thedyrt.com/sitemaps/campgrounds.xml.gz"

@app.route("/updated-campgrounds", methods=["GET"])
def get_updated_campgrounds():
    try:
        logger.info("Starting to fetch updated campgrounds.")
        
        previous_data = load_previous_urls_from_db()
        logger.debug(f"Loaded {len(previous_data)} previous campground entries from DB.")

        root = download_and_parse_sitemap(SITEMAP_URL)
        updated_data = get_updated_entries(root, previous_data)
        logger.debug(f"Found {len(updated_data)} updated entries in sitemap.")

        updated_data_with_names = update_names_for_urls(updated_data)
        logger.info("Updated campground names fetched.")

        formatted_data = {}
        for url, campground_data in updated_data_with_names.items():
            try:
                corrected_data = {
                    "id": str(uuid.uuid4()),
                    "type": campground_data.get('type'),
                    "links": CampgroundLinks(self=campground_data.get('links')),
                    "name": campground_data.get('name'),
                    "latitude": campground_data.get('latitude'),
                    "longitude": campground_data.get('longitude'),
                    "region-name": campground_data.get('region-name', 'Unknown'),
                    "administrative_area": campground_data.get('administrative-area'),
                    "nearest_city_name": campground_data.get('nearest-city-name'),
                    "accommodation_type_names": campground_data.get('accommodation-type-names', []),
                    "bookable": campground_data.get('bookable', False),
                    "camper_types": campground_data.get('camper-types', []),
                    "operator": campground_data.get('operator'),
                    "photo_url": campground_data.get('photo-url'),
                    "photo_urls": campground_data.get('photo-urls', []),
                    "photos_count": campground_data.get('photos-count', 0),
                    "rating": campground_data.get('rating'),
                    "reviews_count": campground_data.get('reviews-count', 0),
                    "slug": campground_data.get('slug'),
                    "price_low": campground_data.get('price-low'),
                    "price_high": campground_data.get('price-high'),
                    "availability_updated_at": campground_data.get('availability-updated-at'),
                }

                campground = Campground(**corrected_data)

                db_data = {
                    "id": campground.id,
                    "type": campground.type,
                    "links": campground.links.self,
                    "name": campground.name,
                    "latitude": campground.latitude,
                    "longitude": campground.longitude,
                    "region_name": campground.region_name,
                    "administrative_area": campground.administrative_area,
                    "nearest_city_name": campground.nearest_city_name,
                    "accommodation_type_names": campground.accommodation_type_names,
                    "bookable": campground.bookable,
                    "camper_types": campground.camper_types,
                    "operator": campground.operator,
                    "photo_url": str(campground.photo_url) if campground.photo_url else None,
                    "photo_urls": [str(u) for u in campground.photo_urls],
                    "photos_count": campground.photos_count,
                    "rating": campground.rating,
                    "reviews_count": campground.reviews_count,
                    "slug": campground.slug,
                    "price_low": campground.price_low,
                    "price_high": campground.price_high,
                    "availability_updated_at": campground.availability_updated_at,
                }

                try:
                    insert_campground(db_data)
                    logger.info(f"Inserted campground into DB: {campground.name}")
                except Exception as db_err:
                    logger.error(f"DB insert error for {campground.name}: {db_err}")

                formatted_data[f"links: {url}"] = {
                    key: str(value) if isinstance(value, HttpUrl) else value 
                    for key, value in campground.dict().items()
                }

            except ValidationError as e:
                logger.warning(f"Validation error for URL {url}: {e}")
                continue

        logger.info("All updated campgrounds processed successfully.")
        return jsonify({"status": 200})

    except Exception as e:
        logger.exception("An error occurred in get_updated_campgrounds.")
        return jsonify({"error": str(e)}), 500
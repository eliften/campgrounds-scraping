import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from pydantic import HttpUrl
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def create_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info("Veritabanına bağlantı başarılı.")
        return conn
    except Exception as e:
        logging.error(f"Veritabanına bağlanırken hata oluştu: {e}")
        return None

def create_database():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        create_db_query = sql.SQL("CREATE DATABASE {dbname};").format(
            dbname=sql.Identifier(DB_NAME)
        )
        cur.execute(create_db_query)
        logging.info(f"{DB_NAME} veritabanı başarıyla oluşturuldu.")
        cur.close()
        conn.close()
    except Exception as e:
        logging.warning(f"{DB_NAME} veritabanı oluşturulamadı (belki zaten var?): {e}")

def create_table():
    create_table_query = """
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE TABLE IF NOT EXISTS campgrounds (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        type VARCHAR NOT NULL,
        links VARCHAR NOT NULL,
        name VARCHAR NOT NULL,
        latitude DOUBLE PRECISION NOT NULL,
        longitude DOUBLE PRECISION NOT NULL,
        region_name VARCHAR NOT NULL,
        administrative_area VARCHAR,
        nearest_city_name VARCHAR,
        accommodation_type_names TEXT[] NOT NULL,
        bookable BOOLEAN DEFAULT FALSE,
        camper_types TEXT[] NOT NULL,
        operator VARCHAR,
        photo_url VARCHAR,
        photo_urls TEXT[] NOT NULL,
        photos_count INTEGER DEFAULT 0,
        rating DOUBLE PRECISION,
        reviews_count INTEGER DEFAULT 0,
        slug VARCHAR,
        price_low DOUBLE PRECISION,
        price_high DOUBLE PRECISION,
        availability_updated_at TIMESTAMP
    );
    """
    conn = create_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute(create_table_query)
            conn.commit()
            logging.info("Campgrounds tablosu başarıyla oluşturuldu veya zaten mevcut.")
        except Exception as e:
            logging.error(f"Tablo oluşturulurken hata oluştu: {e}")
        finally:
            cur.close()
            conn.close()

def insert_campground(data):
    insert_query = """
    INSERT INTO campgrounds (
        type, links, name, latitude, longitude, region_name, administrative_area,
        nearest_city_name, accommodation_type_names, bookable, camper_types, operator,
        photo_url, photo_urls, photos_count, rating, reviews_count, slug, price_low, price_high, availability_updated_at
    ) VALUES (
        %(type)s, %(links)s, %(name)s, %(latitude)s, %(longitude)s, %(region_name)s, %(administrative_area)s,
        %(nearest_city_name)s, %(accommodation_type_names)s, %(bookable)s, %(camper_types)s, %(operator)s,
        %(photo_url)s, %(photo_urls)s, %(photos_count)s, %(rating)s, %(reviews_count)s, %(slug)s, %(price_low)s, %(price_high)s, %(availability_updated_at)s
    );
    """
    if isinstance(data["links"], HttpUrl):
        data["links"] = str(data["links"])
    if isinstance(data["operator"], HttpUrl):
        data["operator"] = str(data["operator"])
    if isinstance(data["photo_urls"], list):
        data["photo_urls"] = [str(url) for url in data["photo_urls"]]

    conn = create_connection()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute(insert_query, data)
            conn.commit()
            logging.info(f"{data.get('name', 'Bilinmeyen')} kamp alanı başarıyla eklendi.")
        except Exception as e:
            logging.error(f"Veri eklenirken hata oluştu: {e}")
        finally:
            cur.close()
            conn.close()

def load_previous_urls_from_db() -> Dict[str, dict]:
    query = "SELECT * FROM campgrounds"
    conn = create_connection()
    result = {}
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor) 
        try:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                url = row["links"]
                result[url] = row
            logging.info(f"Veritabanından {len(result)} kayıt yüklendi.")
        except Exception as e:
            logging.error(f"Veriler yüklenirken hata oluştu: {e}")
        finally:
            cur.close()
            conn.close()
    return result

import logging
import schedule
import time
from threading import Thread
from src.api.api import app
from src.db import db_methods

def start_logging(log_file="app.log"):
    logging.basicConfig(
        filename=log_file, 
        level=logging.DEBUG, 
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info("Logging started.")

def update_data():
    try:
        logging.info("Starting scheduled update.")
        
        db_methods.create_connection()
        logging.info("Database connection established.")

        db_methods.create_database()
        logging.info("Database created (if not already existing).")
        
        db_methods.create_table()
        logging.info("Table created (if not already existing).")
        
        logging.info("Data update completed.")
        
    except Exception as e:
        logging.error(f"Error during scheduled update: {e}")

def run_flask_app():
    app.run(host='0.0.0.0', port=5000)

def run_schedule():
    # Schedule every 2 hours for the update task
    schedule.every(2).hours.do(update_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__": 
    start_logging("app.log")
    
    db_methods.create_connection()
    logging.info("Database connection established.")
    
    db_methods.create_database()
    logging.info("Database created (if not already existing).")
    
    db_methods.create_table()
    logging.info("Table created (if not already existing).")
    
    logging.info("Scheduled updates set for every 2 hours.")
    
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()
    logging.info("Flask app started in a separate thread.")
    
    schedule_thread = Thread(target=run_schedule)
    schedule_thread.start()

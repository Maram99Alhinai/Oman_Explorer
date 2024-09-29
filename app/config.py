import sys
import os
from dotenv import load_dotenv
import logging


def load_configurations(app):
    load_dotenv(override=True)
    
    #Genreal Config
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")
    
    # Database Config
    app.config['DB_USER'] = os.environ.get('DB_USER', 'root')
    app.config['DB_PASS'] = os.environ.get('DB_PASS')
    app.config['DB_NAME'] = os.environ.get('DB_NAME', 'sohail_db')
    app.config['DB_HOST'] = os.environ.get('DB_HOST')  
    app.config['DB_PORT'] = os.environ.get('DB_PORT', '3307')  
    
    # Update the SQLALCHEMY_DATABASE_URI to use TCP/IP
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{app.config['DB_USER']}:{app.config['DB_PASS']}@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
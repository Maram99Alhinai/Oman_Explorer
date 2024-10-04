import logging
from app import create_app
import os
from pathlib import Path

# Create data directory in your project root
current_dir = Path(__file__).parent
data_dir = current_dir / "data"

# Create the data directory if it doesn't exist
data_dir.mkdir(exist_ok=True)

# Set the threads database path
os.environ['THREADS_DB_PATH'] = str(data_dir / "threads_db")


app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8000)

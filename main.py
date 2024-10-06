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
    port = int(os.environ.get("PORT", 8080))  # Use PORT env variable or default to 8080
    logging.info(f"Flask app started on port {port}")
    app.run(host="0.0.0.0", port=port)

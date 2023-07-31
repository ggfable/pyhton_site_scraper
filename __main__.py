import logging
import uvicorn
from routes import app

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.info("Starting the application...")
    uvicorn.run("routes:app", host="0.0.0.0", port=5000, workers=4, log_level="debug")
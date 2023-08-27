import logging
import uvicorn
from routes import app

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info("Starting the application...")
    uvicorn.run("routes:app", host="0.0.0.0", port=5000, workers=4, log_level="debug")
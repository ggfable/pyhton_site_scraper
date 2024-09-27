import logging
import uvicorn
from routes import app

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d",
        handlers=[logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    logger.info("Starting the application...")

    try:
        uvicorn.run(
            "routes:app", host="0.0.0.0", port=8123, workers=10, log_level="debug"
        )
        logger.info("Application is started.")
    except Exception as e:
        logger.exception("Error during startup: %s", str(e))

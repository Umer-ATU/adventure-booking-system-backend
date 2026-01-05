import logging
import sys

from app.core.config import settings

def setup_logging():
    """
    Configure logging for the application.
    """
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set log levels for specific libraries to reduce noise
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.info(f"Logging setup complete for {settings.PROJECT_NAME}")

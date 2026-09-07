import logging
from pathlib import Path

from config.config import LOG_DIR


def setup_logger():
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    log_file = Path(LOG_DIR) / "app.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)
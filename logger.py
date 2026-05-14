import logging
import os
import sys
from datetime import datetime
from pathlib import Path


LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_DIR = Path(os.environ.get("LOG_DIR", Path.cwd() / "logs"))
LOG_FILE_PATH = LOG_DIR / LOG_FILE
_configured = False


def setup_logging() -> None:
    global _configured
    if _configured:
        return

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s")
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    stream_handler = logging.StreamHandler(sys.stdout)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)

from pathlib import Path
from loguru import logger
import sys

def setup_logging(
    log_file: str = "logs/app.jsonl",
    console_level: str = "INFO",
    file_level: str = "DEBUG",
):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    logger.remove()

    logger.add(
        sys.stdout,
        level=console_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    logger.add(
        log_file,
        level=file_level,
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
        enqueue=True,
        serialize=True,
    )
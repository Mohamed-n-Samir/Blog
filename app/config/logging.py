import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Prevent duplicate handlers on reload
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
"""
Centralised logger factory for all A4 modules.

USAGE:
  from utils.logger import setup_logger
  logger = setup_logger("FusionEngine")
  logger = setup_logger("FUSION_VisualAdapter")

DESIGN:
  - One StreamHandler per named logger (guards against duplicate handlers
    when modules are imported multiple times in the same process).
  - Format: timestamp | level | name | message
  - Level: INFO by default. Modules call logger.warning() / logger.error()
    / logger.critical() for elevated severity.

SCALABILITY NOTES:
  - Replace StreamHandler with a RotatingFileHandler or cloud logging
    handler (e.g. Google Cloud Logging) when deploying to production.
  - Add a JSON formatter when structured log ingestion (e.g. Datadog) is needed.
  - Log level can be overridden per environment via the LOG_LEVEL env var.
"""

import logging
import os

_LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
if _LOG_LEVEL not in _VALID_LEVELS:
    _LOG_LEVEL = "INFO"



def setup_logger(name: str) -> logging.Logger:
    """
    Create or retrieve a named logger with a consistent format.

    Guards against duplicate handlers, safe to call multiple times
    with the same name in the same Python process.

    Args:
        name: Logger name, e.g. "FusionEngine", "FUSION_VisualAdapter".
              Appears in every log line for easy filtering.

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, _LOG_LEVEL, logging.INFO))

        handler   = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent log records from propagating to the root logger
        # to avoid duplicate output when running under uvicorn or pytest
        logger.propagate = False

    return logger

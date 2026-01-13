import logging

logger = logging.getLogger(__package__)


def get_float_safe(value) -> float | None:
    try:
        return float(value)
    except Exception:
        logger.warning(f"Couldn't convert to float {value}")

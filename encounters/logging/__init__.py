import logging
import re

# cant put the full ISO format here, because of a flaw in the logging module's
# handling of milliseconds (instead, must use '%(msecs)' in the main format
ISOFORMAT = "%Y-%m-%dT%H:%M:%S"


class MaskingFormatter(logging.Formatter):
    def format(self, record):
        s = logging.Formatter.format(self, record)
        s = re.sub(r"\w+@\w+\.\w\w\w", "#####@#####.###", s)
        s = re.sub(r"\d\d\d[-\.]\d\d\d[-\.]\d\d\d\d", "###-###-####", s)
        return s


def setup_logging(level=logging.DEBUG):
    """
    Should be called once.
    """
    if not isinstance(level, str):
        level = logging.getLevelName(level)
    fmt = "%(asctime)s.%(msecs)03d %(levelname)s %(name)s %(message)s"
    logging.basicConfig(
        # format=fmt,
        level=logging.DEBUG,
        datefmt=ISOFORMAT,
    )

    for handler in logging.root.handlers:
        handler.setFormatter(
            MaskingFormatter(
                fmt=fmt,
                datefmt=ISOFORMAT,
            )
        )

import logging
from typing import Union


class BaseLogger:
    """Create the base logger object"""
    level: Union[str, int] = logging.INFO

    def __init__(self, *args, **kwargs):
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup up logger"""

        # Create logger
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(self.level)

        if not logger.handlers:
            # Create console handler and set level to debug
            ch = logging.StreamHandler()
            ch.setLevel(self.level)

            # Create formatter
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s [%(name)s] - %(message)s')

            # Add formatter to ch
            ch.setFormatter(formatter)

            # Add ch to logger
            logger.addHandler(ch)

        return logger

import os
import inspect
import logging
import colorlog

from pathlib import Path
from datetime import datetime

NOTICE = 25  # Value between WARNING (30) and INFO (20)


class UniLogger:
    """包含时间和 caller frame的 logger utils

    VERSION: 2023.06.11 (JUNE)

    >>> logger = UniLogger("test", logger_name=__name__)
    >>> logger.info("test")


    (Use in a utils:)

    if logger is not None:
        self.logger = logger
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)
    """

    def __init__(self, output_dir: str = "logs", file_suffix: str = "log", verbose: bool = True,
                 logger_name: str = None, write_log: bool = True):
        """
        Initialize an instance of UniLogger.

        :param output_dir: directory to saves the log file
        :param file_suffix: suffix of the log file
        :param verbose: if True, set the log level to DEBUG; otherwise, set to INFO
        :param logger_name: name of the logger
        :param write_log: if True, write the log to a file; otherwise, only print to console
        """

        self.verbose = verbose
        self.write_log = write_log

        handlers = []

        if self.write_log:
            self.output_dir = Path(output_dir)
            self.log_file_suffix = file_suffix
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = (
                    self.output_dir
                    / f"{self.log_file_suffix}_{datetime.now().strftime('%Y%m%d')}.log"
            )
            handlers.append(logging.FileHandler(self.log_file, mode="a", encoding="utf-8"))

        # Create a color handler
        color_handler = colorlog.StreamHandler()
        color_handler.setFormatter(
            colorlog.ColoredFormatter(
                fmt='%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                },
            )
        )
        handlers.append(color_handler)

        if verbose:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        self.logger = logging.getLogger(logger_name if logger_name else self.__class__.__name__)
        self.logger.setLevel(log_level)

        # Check if handlers already exist before adding them; prevents duplicate handlers in Jupyter notebooks
        if not self.logger.hasHandlers():
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            for handler in handlers:
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

        logging.addLevelName(NOTICE, "NOTICE")

    def log(self, log_level: str, message: str):
        level = getattr(logging, log_level.upper(), logging.INFO)

        # Get the caller function information
        caller_frame = inspect.currentframe().f_back.f_back  # Skip 'log' function frame
        caller_func_name = caller_frame.f_code.co_name

        # Check if called from a utils
        if "self" in caller_frame.f_locals:
            caller_class_name = caller_frame.f_locals["self"].__class__.__name__
        else:
            caller_class_name = None

        # Include the caller function name in the message
        if caller_class_name:
            full_message = f"{caller_class_name}.{caller_func_name}: {message}"
        else:
            full_message = f"{caller_func_name}: {message}"

        self.logger.log(level, full_message)

    def notice(self, message: str):
        """
        using INFO log level but with a checkmark √
        """
        self.log("NOTICE", "✅ " + message)

    def warning(self, message: str):
        self.log("WARNING", "⚠️ " + message)

    def error(self, message: str):
        self.log("ERROR", "❌ " + message)

    def info(self, message: str):
        self.log("INFO", message)

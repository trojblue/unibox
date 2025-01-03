import logging
import colorlog
import inspect
import os
from pathlib import Path
from datetime import datetime
import sys
import colorama


NOTICE = 25  # Value between WARNING (30) and INFO (20)
logging.addLevelName(NOTICE, "NOTICE")


class UniLogger:
    """
    A logger that:
      1) Uses colorlog for console color.
      2) Writes an optional log file.
      3) Shows the caller's class and method.
      4) Conditionally includes file paths for specific log levels.
      5) Detects if console supports color and allows disabling colors.
    """

    def __init__(
        self,
        output_dir: str = "logs",
        file_suffix: str = "log",
        verbose: bool = True,
        logger_name: str = None,
        write_log: bool = True,
        shorten_levels: int = 2,  # how many path parts to show for debug logs
        use_color: bool = True,  # manually enable/disable color
    ):
        self.verbose = verbose
        self.write_log = write_log
        self.shorten_levels = shorten_levels

        # Determine if console supports color
        self.supports_color = self._detect_color_support() if use_color else False

        self.logger = logging.getLogger(logger_name if logger_name else self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

        # Prepare handlers
        handlers = []

        # Optional file handler
        if self.write_log:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            log_file = output_path / f"{file_suffix}_{datetime.now().strftime('%Y%m%d')}.log"
            fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            handlers.append(fh)

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        handlers.append(ch)

        # Add handlers to logger
        if not self.logger.hasHandlers():
            for h in handlers:
                self.logger.addHandler(h)

        self._setup_formatters()

    def _setup_formatters(self):
        """
        Sets colorlog for console and a simpler format for file logs.
        """
        console_format = (
            "%(asctime)s [%(levelname)s] %(my_func)s: %(message)s%(extra_path)s"
        )
        date_format = "%Y-%m-%d %H:%M:%S"

        if self.supports_color:
            color_formatter = colorlog.ColoredFormatter(
                "%(log_color)s" + console_format,
                datefmt=date_format,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "NOTICE": "bold_green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        else:
            color_formatter = logging.Formatter(console_format, date_format)

        # Format for file logs
        file_format = (
            "%(asctime)s [%(levelname)s] %(my_func)s: %(message)s%(extra_path)s"
        )
        file_formatter = logging.Formatter(file_format, date_format)

        # Apply to each handler
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setFormatter(color_formatter)
            else:
                handler.setFormatter(file_formatter)

    def _shorten_path(self, path_str: str, levels: int = 2) -> str:
        """
        Return a shortened path for display.
        """
        parts = path_str.strip("/").split("/")
        return "/" + "/".join(parts[-levels:]) if len(parts) > levels else "/" + "/".join(parts)

    def _detect_color_support(self) -> bool:
        """
        Detects if the console supports color.
        """
        # Check if running in Jupyter or IPython
        try:
            from IPython import get_ipython

            if get_ipython():
                return True
        except ImportError:
            pass

        # Check for TTY and colorama initialization
        if sys.stdout.isatty():
            try:
                colorama.init()  # Initialize colorama for Windows
                return True
            except ImportError:
                pass

        return False

    def log(self, level_name: str, message: str):
        """
        Log with custom formatting based on log level.
        """
        level = getattr(logging, level_name.upper(), logging.INFO)

        # Skip frames to find real caller
        caller_frame = inspect.currentframe().f_back.f_back
        method_name = caller_frame.f_code.co_name
        class_name = None

        if "self" in caller_frame.f_locals:
            class_name = caller_frame.f_locals["self"].__class__.__name__

        if class_name:
            full_func_name = f"{class_name}.{method_name}"
        else:
            full_func_name = method_name

        full_path = os.path.abspath(caller_frame.f_code.co_filename)
        short_path = self._shorten_path(full_path, self.shorten_levels)
        lineno = caller_frame.f_lineno

        # Conditionally include the path for debug, warning, error, critical levels
        if level in [logging.DEBUG, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            extra_path = f" {short_path}:{lineno}"
        else:
            extra_path = ""

        # Provide custom fields in `extra`
        extra = {
            "my_func": full_func_name,
            "my_lineno": lineno,
            "extra_path": extra_path,
        }

        # Log using extra fields
        self.logger.log(level, message, extra=extra)

    def info(self, message: str):
        self.log("INFO", message)

    def debug(self, message: str):
        self.log("DEBUG", message)

    def warning(self, message: str):
        self.log("WARNING", f"⚠️ {message}")

    def error(self, message: str):
        self.log("ERROR", f"❌ {message}")

    def notice(self, message: str):
        self.log("NOTICE", f"✅ {message}")

    def critical(self, message: str):
        self.log("CRITICAL", f"🔥 {message}")

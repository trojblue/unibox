import inspect
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import colorama
import colorlog

NOTICE = 25  # Value between WARNING (30) and INFO (20)
logging.addLevelName(NOTICE, "NOTICE")


def _resolve_log_dir() -> str:
    """Resolve the appropriate log directory based on environment and platform."""
    env = os.getenv('UNIBOX_LOG_DIR')
    if env:
        return env

    if os.name == 'nt':  # Windows
        base = (os.getenv('LOCALAPPDATA')
                or os.getenv('APPDATA')
                or os.path.expanduser('~'))
        return os.path.join(base, 'unibox', 'logs')

    # POSIX systems (Linux, macOS, etc.)
    base = os.getenv('XDG_CACHE_HOME') or os.path.join(os.path.expanduser('~'), '.cache')
    return os.path.join(base, 'unibox', 'logs')


class UniLogger:
    """A logger that:
    1) Uses colorlog for console color.
    2) Writes an optional log file without color.
    3) Shows the caller's class and method.
    4) Conditionally includes file paths for specific log levels.
    5) Detects if console supports color and allows disabling colors.
    """

    def __init__(
        self,
        output_dir: str = "logs",
        file_suffix: str = "log",
        verbose: bool = False,
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
        self.handlers = []

        # Optional file handler
        if self.write_log:
            # Use resolved log directory if default output_dir is used
            if output_dir == "logs":
                log_dir = _resolve_log_dir()
            else:
                log_dir = output_dir

            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"{file_suffix}_{datetime.now().strftime('%Y%m%d')}.log")
            fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            self.handlers.append(fh)

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        self.handlers.append(ch)

        # Add handlers to logger
        if not self.logger.hasHandlers():
            for h in self.handlers:
                self.logger.addHandler(h)

        self._setup_formatters()

    def _setup_formatters(self):
        console_format = "%(asctime)s [%(levelname)s] %(my_func)s: %(message)s%(extra_path)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # 1) If console supports color, use colorlog for the console handler:
        if self.supports_color:
            console_formatter = colorlog.ColoredFormatter(
                "%(log_color)s" + console_format,
                datefmt=date_format,
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "white",
                    "NOTICE": "bold_green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        else:
            console_formatter = logging.Formatter(console_format, date_format)

        # 2) Plain-text formatter for the file handler:
        file_format = "%(asctime)s [%(levelname)s] %(my_func)s: %(message)s%(extra_path)s"
        file_formatter = logging.Formatter(file_format, date_format)

        # 3) Assign them:
        for handler in self.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setFormatter(file_formatter)
            else:
                handler.setFormatter(console_formatter)

    def _shorten_path(self, path_str: str, levels: int = 2) -> str:
        """Return a shortened path for display."""
        parts = path_str.strip("/").split("/")
        return "/" + "/".join(parts[-levels:]) if len(parts) > levels else "/" + "/".join(parts)

    def _detect_color_support(self) -> bool:
        """Detects if the console supports color."""
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
        """Log with custom formatting based on log level."""
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

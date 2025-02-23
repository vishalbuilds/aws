import logging
import os
import inspect
import datetime
import json
import sys
import re
from typing import Dict, Any, Optional

class Logger:
    """Enhanced logging utility with JSON output, metadata, and sensitive data redaction."""

    SENSITIVE_KEYS = ["password", "secret", "token", "apikey", "key", "credentials"]

    def __init__(self, loggername: str = "default_logger_name"):
        """Initializes the logger."""
        self._metadata: Dict[str, Any] = {}
        self._tempdata: Dict[str, Any] = {}

        # Remove existing handlers (Lambda compatibility)
        while logging.root.handlers:
            logging.root.removeHandler(logging.root.handlers[0])

        logging.basicConfig(level=logging.DEBUG, format="%(message)s", stream=sys.stdout)
        self.logger = logging.getLogger(loggername)
        self.set_level("WARNING")
        self.silence_noisy_libs()

    def redact_sensitive_info(self, msg: str) -> str:
        """Redacts sensitive information from log messages."""
        for key in self.SENSITIVE_KEYS:
            msg = re.sub(rf'("?{key}"?\s*[:=]\s*"?)([^"]+)("?)', r'\1[REDACTED]\3', msg, flags=re.IGNORECASE)
        return msg

    def log(self, level: int, msg: str, *args: Any, **kwargs: Any) -> None:
        """Logs message with structured JSON output."""
        if self.logger.isEnabledFor(level):
            msg = self.redact_sensitive_info(msg)
            frame = inspect.currentframe().f_back
            info = inspect.getframeinfo(frame)

            log_entry: Dict[str, Any] = {
                "level": logging.getLevelName(level),
                "message": msg,
                "function": info.function,
                "path": os.path.normpath(info.filename),
                "line": info.lineno,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }

            data = self.get_metadata().copy()
            data.update(self.get_tempdata())
            log_entry.update(data)

            try:
                self.logger._log(level, json.dumps(log_entry, ensure_ascii=False), args, **kwargs)
            except TypeError:
                log_entry["message"] = "Error serializing log message. Original Message: " + msg
                self.logger._log(level, json.dumps(log_entry, ensure_ascii=False), args, **kwargs)

        self._tempdata.clear()

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log(logging.ERROR, msg, *args, **kwargs)

    def fatal(self, msg: str, *args: Any, **kwargs: Any) -> None:
        self.log(logging.FATAL, msg, *args, **kwargs)

    def set_metadata(self, key_values: Optional[Dict[str, Any]]) -> None:
        """Sets metadata for logging."""
        self._metadata = key_values if key_values else {}

    def get_metadata(self) -> Dict[str, Any]:
        """Retrieves metadata."""
        return self._metadata

    def add_metadata(self, key: str, value: Any) -> None:
        """Adds key-value pair to metadata."""
        if key is not None:
            self._metadata[key] = value

    def delete_metadata(self, key: str) -> None:
        """Deletes metadata key."""
        if key is not None and key in self._metadata:
            del self._metadata[key]

    def get_tempdata(self) -> Dict[str, Any]:
        """Retrieves temporary data."""
        return self._tempdata

    def add_tempdata(self, key: str, value: Any) -> None:
        """Adds key-value pair to temporary data."""
        if key is not None:
            self._tempdata[key] = value

    @staticmethod
    def noisy_libs() -> list[str]:
        """Returns a list of noisy libraries."""
        return ["boto3", "botocore"]

    def silence_noisy_libs(self) -> None:
        """Silences noisy libraries by setting their log level to WARNING."""
        for lib in self.noisy_libs():
            logging.getLogger(lib).setLevel(logging.WARNING)

    def set_level(self, level: str) -> None:
        """Sets logging level."""
        log_level = level.upper()

        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if log_level in levels:
            self.info(f"Setting log level to {log_level}")
            self.logger.setLevel(levels[log_level])
        else:
            self.warning(f"Invalid log level '{log_level}'. Using default WARNING level.")
            self.logger.setLevel(logging.WARNING)

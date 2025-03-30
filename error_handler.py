import os
import sys
import logging
import traceback
from typing import Optional
from datetime import datetime

# Default log directory and file
LOG_DIR = "logs"
LOG_FILE = "matrix_rain.log"

# Global exception handler
_original_excepthook = sys.excepthook


def setup_error_handling(log_file: Optional[str] = None) -> None:
    """
    Set up error handling and logging for the application.

    Args:
        log_file (Optional[str]): Path to log file.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR)
        except Exception as e:
            print(f"Warning: Could not create log directory: {e}")

    # Use default log file if none specified
    if log_file is None:
        log_file = os.path.join(LOG_DIR, LOG_FILE)

    # Configure logging
    try:
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Add console handler
        console = logging.StreamHandler()
        console.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        console.setFormatter(formatter)
        logging.getLogger("").addHandler(console)

        # Set global exception handler
        sys.excepthook = _custom_excepthook

    except Exception as e:
        print(f"Warning: Could not configure logging: {e}")
        # Fall back to default exception handling
        sys.excepthook = _original_excepthook


def _custom_excepthook(
    exc_type: type, exc_value: Exception, exc_traceback: traceback
) -> None:
    """
    Custom exception hook to log uncaught exceptions.

    Args:
        exc_type (type): Exception type
        exc_value (Exception): Exception instance
        exc_traceback (traceback): Exception traceback
    """
    # Log the exception
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # Call the original exception hook
    _original_excepthook(exc_type, exc_value, exc_traceback)


def handle_error(error: Exception, additional_info: str = "") -> None:
    """
    Handle an exception by logging it and optionally displaying to the user.

    Args:
        error (Exception): The exception to handle
        additional_info (str): Additional information to log
    """
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Format error message
    error_message = f"{timestamp} - ERROR: {type(error).__name__}: {str(error)}"
    if additional_info:
        error_message += f" - {additional_info}"

    # Log the error
    logging.error(error_message, exc_info=True)

    # Print to console
    print(error_message)

    # Log stack trace
    logging.debug("Stack trace:", exc_info=True)

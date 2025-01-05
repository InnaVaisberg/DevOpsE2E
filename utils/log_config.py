import logging
import os

def configure_logging(log_file):
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Reset existing loggers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w"),  # Clear log file for new run
            logging.StreamHandler()  # Log to console
        ]
    )

def log_test_start(test_name):
    logging.info("=" * 50)
    logging.info(f"Starting Test: {test_name}")

def log_test_end(test_name):
    logging.info(f"Test Finished: {test_name}")
    logging.info("=" * 50)

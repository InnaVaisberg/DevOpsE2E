import os
import logging

def save_screenshot(driver, screenshot_dir, file_name):
    """Save a screenshot with error handling."""
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    screenshot_path = os.path.join(screenshot_dir, file_name)
    try:
        driver.save_screenshot(screenshot_path)
        logging.info(f"Screenshot saved at {screenshot_path}")
    except Exception as e:
        logging.error(f"Failed to save screenshot: {e}")

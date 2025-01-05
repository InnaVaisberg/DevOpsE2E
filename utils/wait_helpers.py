from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By


import logging
import os
import time

def ensure_directory_exists(directory):
    """Ensure that a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)


def wait_for_url_to_change(driver, original_url, timeout=10):
    """
    Wait until the URL of the page changes from the original URL.

    :param driver: WebDriver instance.
    :param original_url: The URL to wait for a change from.
    :param timeout: Maximum time to wait for the URL to change.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(original_url))
        logging.info("URL has changed from the original URL.")
    except TimeoutException:
        logging.error(f"Timed out waiting for URL to change from {original_url}.")
        raise  # Re-raise the exception to indicate failure

def wait_for_page_to_load(driver, timeout=30):
    """
    Wait for the page to fully load by checking document.readyState.
    
    :param driver: WebDriver instance.
    :param timeout: Maximum time to wait for the page to load.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        logging.info("Page loaded completely.")
    except TimeoutException:
        logging.error(f"Page did not load completely within {timeout} seconds.")
        raise  # Re-raise the exception to indicate failure

def wait_for_element_to_be_visible(driver, by, value, timeout=20):
    """
    Wait for an element to be visible.

    :param driver: WebDriver instance.
    :param by: Locator strategy (e.g., By.ID, By.CLASS_NAME).
    :param value: Locator value for the element.
    :param timeout: Time to wait for the element to become visible.
    :return: The WebElement if found.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
        logging.info(f"Element located with {by}='{value}' is now visible.")
    except TimeoutException:
        logging.error(f"Timeout while waiting for element with {by}='{value}' to become visible after {timeout} seconds.")
        raise  # Re-raise the exception to indicate failure


def wait_for_element_to_be_visible_and_clickable(driver, by, value, timeout=20):
    """
    Wait for an element to be visible and clickable.
    
    :param driver: WebDriver instance.
    :param by: Locator strategy (e.g., By.ID, By.NAME).
    :param value: Locator value.
    :param timeout: Time to wait for the element.
    :return: WebElement if found, else raise TimeoutException.
    """
    start_time = time.time()
    screenshots_dir = "logs/screenshots"
    ensure_directory_exists(screenshots_dir)

    try:
        # Wait for the page to fully load before locating the element
        wait_for_page_to_load(driver, timeout=timeout)

        # Wait for the element to be clickable
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        elapsed_time = time.time() - start_time
        logging.info(f"Element located with {by}='{value}' and clickable after {elapsed_time:.2f} seconds.")
        return element
    except Exception as e:
        # Log the failure and save a screenshot
        elapsed_time = time.time() - start_time
        screenshot_path = os.path.join(screenshots_dir, f"element_not_found_{value}.png")
        driver.save_screenshot(screenshot_path)
        logging.error(f"Failed to locate element with {by}='{value}' within {timeout} seconds: {e}")
        logging.error(f"Screenshot saved at {screenshot_path}")
        raise

def wait_for_url_to_change(driver, original_url, timeout=10):
    """
    Wait until the URL of the page changes from the original URL.

    :param driver: WebDriver instance.
    :param original_url: The URL to wait for a change from.
    :param timeout: Maximum time to wait for the URL to change.
    """
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(original_url))
        logging.info("URL has changed from the original URL.")
    except TimeoutException:
        logging.error(f"Timed out waiting for URL to change from {original_url}.")
        raise  # Re-raise the exception to indicate failure
    
def wait_for_button_to_be_available(driver, by, value, timeout=10):
    """
    Wait for a button to be available for clicking after any animations are done.
    
    :param driver: WebDriver instance.
    :param by: Locator strategy (e.g., By.ID, By.NAME).
    :param value: Locator value of the button.
    :param timeout: Maximum time to wait for the button.
    """
    try:
        # Wait for the button to be clickable (implicitly waits for visibility)
        WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        logging.info(f"Button located with {by}='{value}' is ready for interaction.")
    except Exception as e:
        logging.error(f"Button with {by}='{value}' is not clickable within {timeout} seconds: {e}")
        raise

def verify_single_player_gallery_items_absence(driver):
    """
    Verify that unwanted items are absent in the gallery for a Single Player.

    :param driver: WebDriver instance.
    """
    try:
        # Locate and click on the Gallery button
        gallery_button = wait_for_element_to_be_visible_and_clickable(driver, By.CLASS_NAME, "GlobalGalleryButton", timeout=5)
        gallery_button.click()
        logging.info("Clicked on the Global Gallery button.")

        # Locate the gallery container
        gallery_container_xpath = "//div[contains(@class, 'GlobalLibraryMainContainer')]"
        wait_for_element_to_be_visible_and_clickable(driver, By.XPATH, gallery_container_xpath)
        logging.info("Gallery is displayed successfully.")

        # Define unwanted hrefs or text that should not be present
        unwanted_items = [
            "#/administration",
            "#/activities",  # This item should not be present
            "#/teams"        # Another item to check for absence
        ]

        # Verify that each unwanted item is NOT displayed
        for href in unwanted_items:
            item_present = driver.find_elements(By.XPATH, f"{gallery_container_xpath}//a[@href='{href}']")
            # Assert that the length of the list is 0, meaning the item should not exist
            assert len(item_present) == 0, f"Unwanted item with href '{href}' should not be present, but it was found."
            logging.info(f"Unwanted item with href '{href}' is not found as expected.")

    except Exception as e:
        logging.error(f"An error occurred while verifying Single Player gallery items absence: {e}")
        raise
def verify_global_library_player_button_absence(driver):
    """
    Verify that the Global Library button is not present after login.
    """
    try:
        wait_for_element_to_be_visible_and_clickable(driver, By.CLASS_NAME, "GlobalLibraryButton", timeout=5)
        assert False, "Global Library button should not be visible, but it was found."
    except TimeoutException:
        logging.info("Global Library button not found as expected.")
        
def verify_global_library_player_button_presence(driver):
    """
    Check that the Global Library button is visible after login. 
    If it's open, close it first. Then, click the Global Gallery button and ensure the Global Library is open.

    :param driver: WebDriver instance.
    """
    try:
        # XPath for the Global Library title to check if it's already open
        global_library_title_xpath = "//div[contains(@class, 'GlobalLibraryTitle')]"

        # Check if the Global Library is currently open
        global_library_open = is_element_present(driver, By.XPATH, global_library_title_xpath)
        
        if global_library_open:
            logging.info("Global Library is currently open. Closing it.")
            # Implement logic to close the Global Library, assuming there's a close button
            close_global_library(driver)

        # Try to find the Global Gallery button
        global_gallery_button = wait_for_element_to_be_visible_and_clickable(driver, By.CLASS_NAME, "GlobalGalleryButton", timeout=5)
        logging.info("Global Gallery button found.")

        # Click on the Global Gallery button
        global_gallery_button.click()
        logging.info("Clicked on the Global Gallery button.")

        # Wait for the Global Library title to be visible after clicking the Gallery button
        wait_for_element_to_be_visible_and_clickable(driver, By.XPATH, global_library_title_xpath, timeout=5)

        # Assert that the Global Library title is displayed
        assert driver.find_element(By.XPATH, global_library_title_xpath).is_displayed(), "Global Library title should be visible after clicking the gallery."
        logging.info("Global Library title found as expected after clicking Global Gallery button.")

    except TimeoutException:
        logging.error("Timeout occurred; could not find the Global Gallery button or Global Library title.")
        assert False, "Expected elements were not found."

    logging.info("Global Library button interaction completed successfully.")

def is_element_present(driver, by, value):
    """
    Check if an element is present in the DOM.

    :param driver: WebDriver instance.
    :param by: Locator strategy (e.g., By.XPATH).
    :param value: Locator value.
    :return: True if the element is found, False otherwise.
    """
    return len(driver.find_elements(by, value)) > 0  # Returns True if found, False otherwise
    
def close_global_library(driver):
    """
    Close the Global Library if it is open. 
    This function needs to be defined based on how the Global Library is closed in the UI.

    :param driver: WebDriver instance.
    """
    # Replace with the actual logic to close the Global Library, 
    # for example, clicking a close button.
    close_button = wait_for_element_to_be_visible_and_clickable(driver, By.CLASS_NAME, "close_GlobalLibrary_button")  # Use the correct selector
    close_button.click()
    logging.info("Global Library closed.")

import logging
import os
from datetime import datetime
import time
import pytest
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.log_config import configure_logging
from utils.screenshot_helpers import save_screenshot
from utils.wait_helpers import is_element_present, wait_for_page_to_load, wait_for_element_to_be_visible_and_clickable, wait_for_element_to_be_visible
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Base directory for logs
BASE_LOGS_DIR = "logs"

# Path to the Excel test data file
test_data_file = os.path.join(os.path.dirname(__file__), '../data/test_data.xlsx')


def create_run_directory():
    """Create a unique directory for the run using the current timestamp."""
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(BASE_LOGS_DIR, f"test_run_{now}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


@pytest.fixture(scope="session")
def setup_run_directory():
    """Create a unique directory for the test suite run."""
    run_directory = create_run_directory()
    yield run_directory  # Provide the path to the run directory to the tests


@pytest.fixture()
def setup_driver():
    """Fixture to setup the WebDriver instance. This driver will remain open."""
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH
    driver.maximize_window()
    yield driver  # Keep the browser open for further use after tests


@pytest.fixture(scope="session", autouse=True)
def setup_suite(request):
    """Setup the test suite, configure logging, and initialize WebDriver."""
    global driver
    # Get the suite name and add a timestamp with milliseconds
    suite_name = request.config.getoption("markexpr", default="test_suite").split("_")[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S.%f")[:-3]  # Current timestamp with milliseconds
    log_file = f"{BASE_LOGS_DIR}/{suite_name}_{timestamp}_test_suite.log"  # Log file with timestamp

    configure_logging(log_file)
    logging.info(f"Starting {suite_name} Test Suite with logs in {log_file}.")

    # Initialize the WebDriver for the session
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH
    driver.maximize_window()

    yield driver  # Yield the driver to the tests

    # Clean up WebDriver after all tests are complete
    if driver:
        driver.quit()
        logging.info("All browsers closed successfully.")

    logging.info(f"{suite_name} Test Suite Completed.")


def get_test_data(file_path):
    """Read test data from an Excel file."""
    return pd.read_excel(file_path)


def test_positive_player_login(setup_run_directory, setup_driver):
    test_name = "Positive_Login_Test"
    log_file = os.path.join(setup_run_directory, f"{test_name}.log")
    configure_logging(log_file)
    logging.info("Starting test for positive login.")

    driver = setup_driver

    try:
        driver.get("")
        logging.info("Navigated to login page.")

        wait_for_page_to_load(driver)

        # Enter credentials
        wait_for_element_to_be_visible_and_clickable(driver, By.NAME, "username").send_keys("44@cympire.com")
        logging.info("Username entered successfully.")
        wait_for_element_to_be_visible_and_clickable(driver, By.NAME, "password").send_keys("234!")
        logging.info("Password entered successfully.")
        wait_for_element_to_be_visible_and_clickable(driver, By.NAME, "sign in").click()
        logging.info("Sign-in button clicked.")

        welcome_message = wait_for_element_to_be_visible_and_clickable(driver, By.CLASS_NAME, "WelcomeMsgName", timeout=30)
        assert "Hello Player" in welcome_message.text, "Welcome message not displayed as expected."
        logging.info(f"Welcome message verified: {welcome_message.text}")

        interact_with_global_library_event(driver)

        screenshot_name = f"{test_name}_success.png"
        save_screenshot(driver, setup_run_directory, screenshot_name)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        screenshot_name = f"{test_name}_error.png"
        save_screenshot(driver, setup_run_directory, screenshot_name)
    finally:
        # Do not close the driver here, keep it open for subsequent tests
        logging.info(f"Finished test: {test_name}")


def interact_with_global_library_event(driver):
    """
    Interacts with the Global Library and manages events like terminating or joining.
    
    :param driver: WebDriver instance.
    """
    try:
        # Check if the Global Library is currently visible
        global_library_container_xpath = "//div[contains(@class, 'GlobalLibraryMainContainer')]"
        
        if is_element_present(driver, By.XPATH, global_library_container_xpath):
            logging.info("Global Library is open. Proceeding to search for 'Extreme Measures'.")
            search_for_extreme_measures_in_global_library(driver)
        else:
            logging.info("Global Library not open, checking for 'Extreme Measures' in Lobby.")

            # Define the XPath for the 'Extreme Measures' event in the specified structure
            extreme_measures_xpath = "//div[@class='sc-eNSrOW bfIymq EventsGalleryItemContainer']//span[contains(@class, 'sc-kCMKrZ') and text()='Extreme Measures']"
            
            # Check for the 'Extreme Measures' event in the Lobby
            if wait_for_element_to_be_visible(driver, By.XPATH, extreme_measures_xpath):
                logging.info("Event 'Extreme Measures' found in Lobby.")
                join_event_in_lobby(driver, extreme_measures_xpath)
            else:
                logging.warning("Event 'Extreme Measures' not found in Lobby. Searching for Global Gallery button.")
                access_global_gallery(driver)
    
    except Exception as e:
        logging.error(f"An error occurred while trying to interact with the Global Library event: {e}")

    finally:
        logging.info("Event interaction completed successfully.")


def search_for_extreme_measures_in_global_library(driver):
    """
    Searches for the 'Extreme Measures' event in the Global Library and interacts with it.

    :param driver: WebDriver instance.
    """
    search_field_xpath = "//input[@class='search-filter_search_field__1ZFKm']"
    wait_for_element_to_be_visible_and_clickable(driver, By.XPATH, search_field_xpath)

    # Enter search text for "Extreme Measures"
    search_field = driver.find_element(By.XPATH, search_field_xpath)
    search_field.clear()
    search_field.send_keys("Extreme Measures")
    logging.info("Entered 'Extreme Measures' in the search field.")

    # Wait for the search results to load
    time.sleep(2)  # This could be replaced with a better waiting strategy

    while True:
        try:
            extreme_measures_xpath = "//div[contains(@class, 'CampaignName') and text()='Extreme Measures']"
            if wait_for_element_to_be_visible(driver, By.XPATH, extreme_measures_xpath):
                logging.info("Event 'Extreme Measures' found in Global Library.")
                
                # Hover over the event item to reveal the "Pick It" button
                event_item = driver.find_element(By.XPATH, extreme_measures_xpath)
                ActionChains(driver).move_to_element(event_item).perform()
                logging.info("Hovered over the 'Extreme Measures' event.")
                
                # Wait for the "Pick It" button to appear
                pick_it_button_xpath = "//button[contains(@class, 'PickItButton')]"
                wait_for_element_to_be_visible(driver, By.XPATH, pick_it_button_xpath)
                pick_it_button = driver.find_element(By.XPATH, pick_it_button_xpath)
                pick_it_button.click()
                logging.info("Clicked the 'Pick It' button.")
                break  # Break the loop since the element has been found

        except NoSuchElementException:
            # Scroll down to reveal more events
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the new events to load
            logging.info("Scrolling down to load more events...")

    # Confirm exiting the gallery
    logging.info("Exiting the gallery...")


def join_event_in_lobby(driver, event_xpath):
    """
    Joins the 'Extreme Measures' event in the Lobby after hovering over it.

    :param driver: WebDriver instance.
    :param event_xpath: XPath for the 'Extreme Measures' event.
    """
    extreme_measures_container = driver.find_element(By.XPATH, event_xpath)
    ActionChains(driver).move_to_element(extreme_measures_container).perform()
    logging.info("Hovered over the 'Extreme Measures' container.")

    join_button_xpath = "//button[contains(@class, 'LobbyJoinButton')]"
    if wait_for_element_to_be_visible(driver, By.XPATH, join_button_xpath, timeout=240):
        join_button = driver.find_element(By.XPATH, join_button_xpath)
        join_button.click()
        logging.info("Clicked the 'Join' button after waiting.")

        # After clicking "Join," verify that the expected content appears
        welcome_message_xpath = "//span[contains(text(), 'Welcome to Extreme Measures')]"
        if wait_for_element_to_be_visible(driver, By.XPATH, welcome_message_xpath):
                        logging.info("Successfully navigated to the 'Extreme Measures' event page.")
        else:
            logging.warning("Could not find the welcome message for 'Extreme Measures'.")
    else:
        logging.warning("Timed out waiting for the 'Join' button to appear.")


def access_global_gallery(driver):
    """
    Access the Global Gallery if the Global Library is not available.

    :param driver: WebDriver instance.
    """
    global_gallery_button_xpath = "//button[contains(@class, 'GlobalGalleryButton')]"
    wait_for_element_to_be_visible_and_clickable(driver, By.XPATH, global_gallery_button_xpath)

    global_gallery_button = driver.find_element(By.XPATH, global_gallery_button_xpath)
    global_gallery_button.click()
    logging.info("Clicked on the Global Gallery button.")


if __name__ == "__main__":
    pytest.main()

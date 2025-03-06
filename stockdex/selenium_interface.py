import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from stockdex.lib import get_user_agent


class selenium_interface:
    def __init__(self, use_custom_user_agent: bool = False):
        # Set up Selenium to use Chrome in headless mode
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Ensure GUI is off
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        # add the package insallation path as base
        self.chrome_options.binary_location = os.path.join(
            os.path.dirname(__file__), "chromedriver_linux64"
        )
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--start-maximized")
        if use_custom_user_agent:
            self.chrome_options.add_argument(f"user-agent={get_user_agent}")

    def get_html_content(self, url: str) -> str:
        """
        Method to fetch the HTML content of a webpage using Selenium

        Args:
        ----------------
        url (str): URL of the webpage

        Returns:
        ----------------
        str: HTML content of the webpage in prettified format
        """
        # Initialize WebDriver
        driver = webdriver.Chrome(options=self.chrome_options)
        # Fetch the webpage
        driver.get(url)

        # Get the page source and close the driver
        page_source = driver.page_source
        driver.quit()

        # Use Beautiful Soup to parse the HTML content
        return BeautifulSoup(page_source, "html.parser")

    def click_on_element(
        self, xpath: str, driver: webdriver.Chrome, wait_time: int = 3
    ):
        """
        Method that clicks on an element
        """
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        element.click()

    def just_etf_get_html_after_click(
        self, url: str, button_xpath: str
    ) -> BeautifulSoup:
        """
        Opens a webpage, clicks a button and returns the updated HTML.
        It is specifically designed for JustETF module.

        Args:
        ----------------
        url (str): The URL of the page to load.
        button_xpath (str): The XPath of the button to click.
        wait_time (int): The time to wait after clicking for the page to update.

        Returns:
        ----------------
        BeautifulSoup: Parsed HTML after the button click.
        """
        driver = webdriver.Chrome(options=self.chrome_options)
        driver.get(url)

        # close the cookie consent popup
        x_path = '//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'
        self.click_on_element(x_path, driver)

        self.click_on_element(button_xpath, driver)

        return BeautifulSoup(driver.page_source, "html.parser")

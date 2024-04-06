import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class selenium_interface:
    def __init__(self):
        # Set up Selenium to use Chrome in headless mode
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Ensure GUI is off
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.binary_location = os.path.join(
            os.getcwd(), "chromedriver_linux64"
        )
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--disable-extensions")
        self.chrome_options.add_argument("--start-maximized")

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

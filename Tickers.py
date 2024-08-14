# Necessary imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import json

# Set up Global WebDriver
driver = webdriver.Chrome()


def main():
    
    SP_tickers = get_SP_tickers()
    print("SP Tickers fetched")
    NYSE_tickers = get_NYSE_tickers()
    print("NYSE Tickers fetched")
    NASDAQ_tickers = get_NASDAQ_tickers()
    print("NASDAQ Tickers fetched")

    # Store all tickers in one list
    tickers = SP_tickers + NYSE_tickers + NASDAQ_tickers
    ALL_tickers = list(set(tickers))

    # Dictionary to store ALL tickers
    all_tickers = {"count": len(ALL_tickers), "tickers": ALL_tickers}

    # Write to JSON file
    with open("data.json", "w") as outfile:
        json.dump(all_tickers, outfile, indent=4)


def scrape_nyse_companies(nyse_tickers):
    
    element_present = EC.presence_of_element_located((By.CLASS_NAME, "table-data"))
    WebDriverWait(driver, 10).until(element_present)

    # Find the table that contains the company data
    table = driver.find_element(By.CLASS_NAME, "table-data")

    # Find all rows in the table body
    rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

    for row in rows:
        # Extract ticker symbol and company name from each row
        ticker = row.find_element(By.TAG_NAME, "a").text
        nyse_tickers.append(ticker)


def get_NYSE_tickers():
    
    # Initialize empty list
    nyse_tickers = []

    # Open the NASDAQ listings page
    nyse_url = "https://www.nyse.com/listings_directory/stock"
    driver.get(nyse_url)
    time.sleep(5)  # Initial wait to ensure page has loaded

    while True:
        scrape_nyse_companies(nyse_tickers)

        # Try to find the 'Next' button
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@rel="next"]'))
            )
            # Click the 'Next' button to go to the next page
            next_button.click()

            # Wait for the new page to load
            time.sleep(1)

        except Exception as e:
            print("No more pages or error occurred:", e)
            break

    return nyse_tickers


def get_SP_tickers():
    
    # Initialize empty list
    sp_tickers = []

    # url for the website
    sp_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    response = requests.get(sp_url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", id="constituents")
    anchor_tags = table.find_all("a", class_="external")

    for anchor in anchor_tags:
        # Add tickers in the list from each row
        sp_tickers.append(anchor.text)

    return sp_tickers


def scrape_nasdaq_companies(nasdaq_tickers):
    
    try:
        element_present = EC.presence_of_element_located(
            (By.CLASS_NAME, "nasdaq-screener__table")
        )
        WebDriverWait(driver, 30).until(element_present)

        # Find the table that contains the company ticker
        table = driver.find_element(By.CLASS_NAME, "nasdaq-screener__table")

        # Find all rows in the table body
        rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        for row in rows:
            # Extract ticker symbol and company name from each row
            wait = WebDriverWait(row, 30)  # Apply the wait specifically to the row

            for i in range(3):  # Retry up to 3 times
                try:
                    ticker_element = wait.until(
                        EC.presence_of_element_located((By.TAG_NAME, "th"))
                    ).find_element(By.TAG_NAME, "a")
                    ticker = ticker_element.text
                    nasdaq_tickers.append(ticker)
                    break  # Exit loop if extraction is successful
                except StaleElementReferenceException:
                    time.sleep(1)  # Wait and retry

    except TimeoutException:
        print("Timeout while waiting for table or rows")


def get_NASDAQ_tickers():
    
    # Initialize empty list
    nasdaq_tickers = []

    # Open the NASDAQ listings page
    nasdaq_url = "https://www.nasdaq.com/market-activity/stocks/screener"
    driver.get(nasdaq_url)
    time.sleep(5)  # Initial wait to ensure page has loaded

    while True:
        scrape_nasdaq_companies(nasdaq_tickers)

        try:
            wait = WebDriverWait(driver, 60)
            # Wait for loader overlay to disappear
            wait.until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "loader-overlay"))
            )

            # Wait for the "Next" button to be clickable
            next_button = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "pagination__next"))
            )

            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            next_button.click()

            # Wait for the new page to load
            time.sleep(5)  # Increased wait to ensure the next page loads fully

        except Exception as e:
            print("No more pages or error occurred:", e)
            break

    return nasdaq_tickers


if __name__ == "__main__":
    main()

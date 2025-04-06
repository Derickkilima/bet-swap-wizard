import requests
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
SPORTYBET_API_URL = "https://www.sportybet.com/api/tz/orders/share/{booking_code}?_t={timestamp}"
BETPAWA_BASE_URL = "https://www.betpawa.co.tz"

# Headers for Sportybet API
SPORTYBET_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.sportybet.com/",
    "Origin": "https://www.sportybet.com",
}

# Function to fetch and parse Sportybet matches


def get_sportybet_matches(booking_code):
    url = SPORTYBET_API_URL.format(
        booking_code=booking_code, timestamp=int(datetime.now().timestamp() * 1000))
    try:
        response = requests.get(url, headers=SPORTYBET_HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f"Failed to fetch Sportybet matches: {e}")
        return []

    matches = []
    for outcome in data.get('data', {}).get('outcomes', []):
        match = {
            'event_id': outcome.get('eventId'),
            'home_team': outcome.get('homeTeamName', '').strip(),
            'away_team': outcome.get('awayTeamName', '').strip(),
            'start_time': outcome.get('estimateStartTime'),
            'odds': {},
            # This will store the selection (Home, Draw, or Away)
            'selection': None
        }
        for market in outcome.get('markets', []):
            if market.get('desc') == '1X2':
                for outcome_data in market.get('outcomes', []):
                    # The desc field directly indicates the selection (Home, Draw, or Away)
                    match['selection'] = outcome_data.get('desc')
                    match['odds'][outcome_data.get('desc')] = float(
                        outcome_data.get('odds', 0))
        matches.append(match)
    return matches

# Function to initialize the Selenium WebDriver


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Maximize the browser window
    # Ensure ChromeDriver is installed
    driver = webdriver.Chrome(options=options)
    return driver

# Function to search for a match and select a bet on Betpawa


def search_and_select_bet(driver, match):
    home_team = match['home_team']
    away_team = match['away_team']
    selection = match['selection']
    try:
        # Step 1: Click the search icon
        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "svg[data-test-id='headerIconSearch']"))
        )
        search_icon.click()

        # Step 2: Enter the team names in the search bar
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='text']"))
        )
        search_bar.clear()
        search_bar.send_keys(f"{home_team} vs {away_team}")
        search_bar.send_keys(Keys.RETURN)

        # Step 3: Wait for the match to appear
        match_container = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 f"//div[contains(@class, 'events-container')]//div[contains(@class, 'teams') and .//p[contains(text(), '{home_team}')] and .//p[contains(text(), '{away_team}')]]//ancestor::div[contains(@class, 'events-container')]")
            )
        )

        # Step 4: Wait for betting options to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, ".//span[contains(@class, 'event-bet-wrapper')]")
            )
        )

        # Step 5: Locate the betting buttons (1, X, 2)
        selection_map = {"Home": "1", "Draw": "X", "Away": "2"}
        bet_option = selection_map[selection]

        # Refined XPath to find the clickable betting button
        bet_button = match_container.find_element(
            By.XPATH, f".//span[contains(@class, 'event-bet-wrapper') and contains(@class, 'bet-price') and .//span[contains(@class, 'event-selection') and text()='{bet_option}']]"
        )
        bet_button.click()

        # Step 6: Verify the bet was added to the bet slip
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.betslip-main:not(.empty-betslip)"))
        )
        logging.info(
            f"Added {selection} ({bet_option}) for {home_team} vs {away_team} to bet slip")
    except Exception as e:
        logging.error(f"Failed to add bet for {home_team} vs {away_team}: {e}")
        raise  # Re-raise the exception for debugging


def get_user_input():
    booking_code = input("Enter the betting code: ").strip()
    site = input("Enter the site (sportybet or betpawa): ").strip().lower()
    return booking_code, site


# Main script
if __name__ == "__main__":
    # Get user input
    booking_code, source_site = get_user_input()
    driver = initialize_driver()

    try:
        # Step 1: Fetch matches from source site (assuming Sportybet for now)
        if source_site == "sportybet":
            matches = get_sportybet_matches(booking_code)
            target_site = BETPAWA_BASE_URL
        else:
            logging.error("Only Sportybet as source is supported for now.")
            exit()

        if not matches:
            logging.error("No matches found.")
            exit()

        # Step 2: Open target site
        driver.get(target_site)

        # Step 3: Add bets to slip
        for match in matches:
            search_and_select_bet(driver, match)

        # Step 4: Generate and display booking code
        new_booking_code = generate_booking_code(driver)
        if new_booking_code:
            print(f"Equivalent Booking Code on Betpawa: {new_booking_code}")
        else:
            logging.error("Failed to generate booking code.")
    finally:
        print(driver.page_source)
        driver.quit()

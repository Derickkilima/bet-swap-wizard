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


def search_and_select_bet(driver, team_name, sportybet_selection):
    try:
        # Click the search icon (use the parent <svg> element)
        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "svg[data-test-id='headerIconSearch']"))
        )
        search_icon.click()

        # Enter the team name in the search bar
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='text']"))
        )
        search_bar.clear()
        search_bar.send_keys(team_name)
        search_bar.send_keys(Keys.RETURN)

        # Wait for the search results to load
        time.sleep(2)

        # Locate the first match's container
        first_match_container = driver.find_element(
            By.XPATH, "//div[contains(., 'Arsenal FC') and contains(., 'PSV Eindhoven')]")

        # Locate the bet buttons (1, X, 2) using their link text
        bet_buttons = {
            "1": first_match_container.find_element(By.XPATH, ".//div[contains(text(), '1')]"),
            "X": first_match_container.find_element(By.XPATH, ".//div[contains(text(), 'X')]"),
            "2": first_match_container.find_element(By.XPATH, ".//div[contains(text(), '2')]"),
        }

        # Click the appropriate button based on the selection
        if sportybet_selection == "Home":
            bet_buttons["1"].click()  # Click the "1" button
        elif sportybet_selection == "Draw":
            bet_buttons["X"].click()  # Click the "X" button
        elif sportybet_selection == "Away":
            bet_buttons["2"].click()  # Click the "2" button
        else:
            logging.error(
                f"Invalid Sportybet selection: {sportybet_selection}")
            return

        logging.info(f"Selected {sportybet_selection} for {team_name}")
    except Exception as e:
        logging.error(f"Failed to search and select bet for {team_name}: {e}")


# Main script
if __name__ == "__main__":
    # Initialize the WebDriver
    driver = initialize_driver()

    try:
        # Step 1: Fetch matches from Sportybet
        sportybet_code = "51GGAS"  # Replace with your Sportybet booking code
        sportybet_matches = get_sportybet_matches(sportybet_code)
        if not sportybet_matches:
            logging.error("No matches found on Sportybet.")
            exit()

        # Step 2: Open Betpawa website
        driver.get(BETPAWA_BASE_URL)

        # Step 3: Search for each match and select the bet on Betpawa
        for match in sportybet_matches:
            team_name = match['home_team']
            # Get the selection (Home, Draw, or Away)
            sportybet_selection = match.get('selection')
            if not sportybet_selection:
                logging.error(
                    f"No selection found for {team_name} in Sportybet response.")
                continue

            search_and_select_bet(driver, team_name, sportybet_selection)

        # Step 4: Generate and extract the booking code
        booking_code = generate_booking_code(driver)
        if booking_code:
            print(f"Booking Code: {booking_code}")
        else:
            logging.error("Failed to generate booking code.")
    finally:
        # Close the WebDriver
        driver.quit()

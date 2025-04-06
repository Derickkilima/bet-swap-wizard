from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

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

# Team name mapping from Sportybet to Betpawa
team_mapping = {
    "Man City": "Manchester City",
    "Wolves": "Wolverhampton Wanderers",
    "Man Utd": "Manchester United",
    "Spurs": "Tottenham Hotspur",
    "Arsenal": "Arsenal FC",
    "Chelsea": "Chelsea FC",
    "Liverpool": "Liverpool FC",
    "Everton": "Everton FC",
    "West Ham": "West Ham United",
    "Ipswich Town": "Ipswich Town FC",
    "Nottingham Forest": "Nottingham Forest FC",
    "Leicester": "Leicester City",
    "Aston Villa": "Aston Villa FC",
    "Brighton": "Brighton & Hove Albion",
    "Southampton": "Southampton FC",
    "Crystal Palace": "Crystal Palace FC",
    "Newcastle": "Newcastle United",
    "Bournemouth": "AFC Bournemouth",
    "Brentford": "Brentford FC",
    "Fulham": "Fulham FC",
}

# Function to map team names from Sportybet to Betpawa


def map_team_name(team_name):
    mapped_name = team_mapping.get(team_name, team_name)
    if team_name not in team_mapping:
        logging.warning(
            f"No mapping found for team: {team_name}. Using original name: {mapped_name}")
    return mapped_name

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
            'market': None,  # e.g., "1X2", "Over/Under 0.5", "BTTS"
            'selection': None,  # e.g., "Home", "Over 0.5", "Yes"
            'odds': {}
        }
        for market in outcome.get('markets', []):
            market_desc = market.get('desc')
            # Handle 1X2 market
            if market_desc == '1X2':
                for outcome_data in market.get('outcomes', []):
                    match['market'] = '1X2'
                    match['selection'] = outcome_data.get(
                        'desc')  # e.g., "Home", "Draw", "Away"
                    match['odds'][outcome_data.get('desc')] = float(
                        outcome_data.get('odds', 0))
            # Handle Over/Under markets dynamically
            elif market_desc == 'Over/Under':
                specifier = market.get('specifier', '')  # e.g., "total=0.5"
                # Default to 2.5 if not specified
                threshold = specifier.split(
                    '=')[1] if '=' in specifier else '2.5'
                for outcome_data in market.get('outcomes', []):
                    # e.g., "Over/Under 0.5"
                    match['market'] = f'Over/Under {threshold}'
                    match['selection'] = outcome_data.get(
                        'desc')  # e.g., "Over 0.5", "Under 2.5"
                    match['odds'][outcome_data.get('desc')] = float(
                        outcome_data.get('odds', 0))
            # Handle Both Teams to Score market (GG/NG)
            elif market_desc == 'GG/NG':
                for outcome_data in market.get('outcomes', []):
                    match['market'] = 'BTTS'
                    match['selection'] = outcome_data.get(
                        'desc')  # e.g., "Yes", "No"
                    match['odds'][outcome_data.get('desc')] = float(
                        outcome_data.get('odds', 0))
        if match['market'] and match['selection']:
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
    home_team = map_team_name(match['home_team'])
    away_team = map_team_name(match['away_team'])
    market = match['market']
    selection = match['selection']
    try:
        # Step 1: Click the search icon
        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "svg[data-test-id='headerIconSearch']"))
        )
        search_icon.click()

        # Step 2: Enter the mapped team names in the search bar
        search_bar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[type='text']"))
        )
        search_bar.clear()
        search_bar.send_keys(f"{home_team} vs {away_team}")
        search_bar.send_keys(Keys.RETURN)

        # Step 3: Locate the div containing the team names and click it
        team_div = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 f"//div[contains(@class, 'events-container prematch')]//div[contains(@class, 'teams') and .//p[contains(text(), '{home_team}')] and .//p[contains(text(), '{away_team}')]]")
            )
        )
        logging.info(
            f"Found team div for {home_team} vs {away_team}: {team_div.get_attribute('outerHTML')}")
        team_div.click()

        # Step 4: Determine the market title to look for
        if market == '1X2':
            market_title = "1X2 | Full Time"
        elif market.startswith('Over/Under'):
            market_title = "Over/Under | Full Time"
        elif market == 'BTTS':
            market_title = "Both Teams To Score | Full Time"
        else:
            raise ValueError(f"Unsupported market: {market}")

        # Step 5: Find the events-container div with the correct market title
        market_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH,
                 f"//div[contains(@class, 'events-container')]//h4[contains(text(), '{market_title}')]//ancestor::div[contains(@class, 'events-container')]")
            )
        )
        logging.info(
            f"Found market container for {market_title}: {market_container.get_attribute('outerHTML')}")

        # Step 6: Locate the betting options (spans) within the market container
        betting_buttons = market_container.find_elements(
            By.XPATH,
            ".//span[contains(@class, 'event-bet-wrapper') and contains(@class, 'bet-price')]"
        )

        # Step 7: Make the selection based on the market type
        if market == '1X2':
            if len(betting_buttons) < 3:
                raise Exception(
                    f"Expected at least 3 betting buttons for {home_team} vs {away_team} (1X2), but found {len(betting_buttons)}")

            selection_map = {"Home": "1", "Draw": "X", "Away": "2"}
            bet_option = selection_map[selection]
            button_index_map = {"1": 0, "X": 1, "2": 2}
            button_index = button_index_map[bet_option]

        elif market.startswith('Over/Under'):
            threshold = market.split(' ')[1]  # e.g., "0.5", "2.5"
            if len(betting_buttons) < 2:
                raise Exception(
                    f"Expected at least 2 betting buttons for {home_team} vs {away_team} (Over/Under {threshold}), but found {len(betting_buttons)}")

            # Construct the expected label: "Over (0.5)" or "Under (2.5)"
            over_or_under = selection.split(' ')[0]  # "Over" or "Under"
            expected_label = f"{over_or_under} ({threshold})"

            # Find the button with the expected label
            button_index = None
            for i, button in enumerate(betting_buttons):
                button_text = button.text.lower()
                if expected_label.lower() in button_text:
                    button_index = i
                    break
            if button_index is None:
                raise Exception(
                    f"Could not find betting button for {expected_label} in Over/Under {threshold} for {home_team} vs {away_team}")

        elif market == 'BTTS':
            if len(betting_buttons) < 2:
                raise Exception(
                    f"Expected at least 2 betting buttons for {home_team} vs {away_team} (BTTS), but found {len(betting_buttons)}")

            button_index_map = {"Yes": 0, "No": 1}
            button_index = button_index_map[selection]

        # Step 8: Click the corresponding button
        bet_button = betting_buttons[button_index]
        logging.info(f"Clicking bet button: {bet_button.text}")
        bet_button.click()

        # Step 9: Verify the bet was added to the bet slip
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.betslip-main:not(.empty-betslip)"))
        )
        logging.info(
            f"Added {market} - {selection} for {home_team} vs {away_team} to bet slip")
    except Exception as e:
        logging.error(f"Failed to add bet for {home_team} vs {away_team}: {e}")
        raise
# Function to generate and extract the booking code


def generate_booking_code(driver):
    try:
        # Step 1: Locate and click the "Booking code" link
        booking_code_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@class, 'underline') and contains(@class, 'booking-code-link') and .//span[contains(text(), 'Booking code')]]")
            )
        )
        booking_code_link.click()

        # Step 2: Wait for the popup to appear and extract the booking code from the h2 element
        booking_code = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h2"))
        ).text

        logging.info(f"Successfully extracted booking code: {booking_code}")
        return booking_code

    except Exception as e:
        logging.error(f"Failed to generate booking code: {e}")
        raise

# API endpoint to convert SportyBet code to Betpawa code


@app.route('/convert', methods=['POST'])
def convert_betting_code():
    try:
        data = request.get_json()
        if not data or 'booking_code' not in data:
            return jsonify({"error": "Missing booking_code"}), 400

        booking_code = data['booking_code']
        logging.info(f"Received booking code: {booking_code}")

        # Initialize Selenium WebDriver
        driver = initialize_driver()
        driver.get("https://www.betpawa.co.tz/")

        # Fetch matches from Sportybet
        matches = get_sportybet_matches(booking_code)
        if not matches:
            driver.quit()
            return jsonify({"error": "No matches found for the given SportyBet booking code"}), 400

        # Process each match
        for match in matches:
            search_and_select_bet(driver, match)

        # Generate and return the Betpawa booking code
        betpawa_code = generate_booking_code(driver)
        driver.quit()

        return jsonify({"converted_code": betpawa_code})
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

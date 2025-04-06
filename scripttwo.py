import requests
from datetime import datetime

# Function to fetch and parse Sportybet matches


def get_sportybet_matches(booking_code):
    url = f"https://www.sportybet.com/api/tz/orders/share/{booking_code}?_t={int(datetime.now().timestamp() * 1000)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.sportybet.com/",
        "Origin": "https://www.sportybet.com",
    }
    response = requests.get(url, headers=headers)

    # # Debugging: Print the status code and raw response
    # print(f"Status Code: {response.status_code}")
    # print(f"Response Text: {response.text}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return []

    matches = []
    for outcome in data['data']['outcomes']:
        match = {
            'event_id': outcome['eventId'],
            'home_team': outcome['homeTeamName'],
            'away_team': outcome['awayTeamName'],
            # Unix timestamp in milliseconds
            'start_time': outcome['estimateStartTime'],
            'odds': {}
        }
        for market in outcome['markets']:
            if market['desc'] == '1X2':
                for outcome_data in market['outcomes']:
                    match['odds'][outcome_data['desc']] = float(
                        outcome_data['odds'])
        matches.append(match)
    return matches

# Function to fetch and parse Betpawa matches


def get_betpawa_matches(booking_code):
    url = f"https://www.betpawa.co.tz/api/sportsbook/v2/booking-number/{booking_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "x-pawa-brand": "betpawa-tanzania",
        "x-pawa-language": "en",
    }

    response = requests.get(url, headers=headers)

    # # Debugging: Print response status and content
    # print(f"Status Code: {response.status_code}")
    # print(f"Response Text: {response.text}")

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return []

    matches = []
    if 'items' in data:
        for item in data['items']:
            match = {
                'event_id': item['event']['id'],
                'home_team': item['event']['name'].split(' - ')[0],
                'away_team': item['event']['name'].split(' - ')[1],
                'start_time': int(datetime.strptime(item['event']['startTime'], "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000),
                'odds': {}
            }

            # ✅ Corrected: Get odds from 'price', NOT 'market'
            if 'price' in item:
                match['odds']['Home'] = item['price'].get('price', 'N/A')
            else:
                print(
                    f"Warning: Missing 'price' data for match {match['home_team']} vs {match['away_team']}")

            matches.append(match)
    else:
        print("Key 'items' not found in Betpawa response.")

    return matches


# Function to find equivalent matches


def find_equivalent_matches(sportybet_matches, betpawa_matches):
    equivalent_matches = []
    for sb_match in sportybet_matches:
        for bp_match in betpawa_matches:
            # Match based on team names and start time
            if (sb_match['home_team'].lower() == bp_match['home_team'].lower() and
                sb_match['away_team'].lower() == bp_match['away_team'].lower() and
                    # Allow 1-minute difference
                    abs(sb_match['start_time'] - bp_match['start_time']) < 60000):
                equivalent_matches.append((sb_match, bp_match))
    return equivalent_matches


# Main script
if __name__ == "__main__":
    sportybet_code = "5BY23P"  # Replace with your Sportybet booking code
    betpawa_code = "73ULLFZ"   # Replace with your Betpawa booking code

    # Fetch matches
    sportybet_matches = get_sportybet_matches(sportybet_code)
    betpawa_matches = get_betpawa_matches(betpawa_code)

    # Find equivalent matches
    equivalent_matches = find_equivalent_matches(
        sportybet_matches, betpawa_matches)

    # Display results
    for sb_match, bp_match in equivalent_matches:
        print(f"Match: {sb_match['home_team']} vs {sb_match['away_team']}")
        print(
            f"Sportybet Odds - Home: {sb_match['odds'].get('Home', 'N/A')}, Draw: {sb_match['odds'].get('Draw', 'N/A')}, Away: {sb_match['odds'].get('Away', 'N/A')}")
        print(f"Betpawa Odds - Home: {bp_match['odds']['Home']}")
        print("------")

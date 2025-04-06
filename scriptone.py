import json

# Sample JSON responses (replace with actual API responses)
sportybet_response = {
    "items": [
        {
            "eventId": "25756857",
            "event": "Lille OSC - Borussia Dortmund",
            "startTime": "2025-03-12T17:45:00Z",
            "marketType": {"name": "1X2 - FT"},
            "selections": [
                {"id": "1", "price": 2.85},
                {"id": "X", "price": 3.50},
                {"id": "2", "price": 2.40}
            ]
        },
        {
            "eventId": "25756863",
            "event": "Arsenal FC - PSV Eindhoven",
            "startTime": "2025-03-12T20:00:00Z",
            "marketType": {"name": "1X2 - FT"},
            "selections": [
                {"id": "1", "price": 1.50},
                {"id": "X", "price": 4.00},
                {"id": "2", "price": 6.00}
            ]
        }
    ]
}

betpawa_response = {
    "items": [
        {
            "event": {
                "id": "25756857",
                "name": "Lille OSC - Borussia Dortmund",
                "startTime": "2025-03-12T17:45:00Z"
            },
            "market": {
                "marketType": {"id": "3743", "name": "1X2 - FT"},
                "price": [
                    {"name": "1", "price": 2.9},
                    {"name": "X", "price": 3.45},
                    {"name": "2", "price": 2.35}
                ]
            }
        },
        {
            "event": {
                "id": "25756863",
                "name": "Arsenal FC - PSV Eindhoven",
                "startTime": "2025-03-12T20:00:00Z"
            },
            "market": {
                "marketType": {"id": "3743", "name": "1X2 - FT"},
                "price": [
                    {"name": "1", "price": 1.49},
                    {"name": "X", "price": 4.10},
                    {"name": "2", "price": 6.10}
                ]
            }
        }
    ]
}

# Function to map the data


def map_bets(sportybet_data, betpawa_data):
    mapped_matches = {}

    # Process SportyBet data
    for match in sportybet_data["items"]:
        event_id = match["eventId"]
        mapped_matches[event_id] = {
            "match": match["event"],
            "startTime": match["startTime"],
            "sportybet": {
                "home_win": match["selections"][0]["price"],
                "draw": match["selections"][1]["price"],
                "away_win": match["selections"][2]["price"]
            },
            "betpawa": {}
        }

    # Process BetPawa data and merge
    for match in betpawa_data["items"]:
        event_id = match["event"]["id"]
        if event_id in mapped_matches:
            mapped_matches[event_id]["betpawa"] = {
                "home_win": match["market"]["price"][0]["price"],
                "draw": match["market"]["price"][1]["price"],
                "away_win": match["market"]["price"][2]["price"]
            }

    return mapped_matches


# Get the mapped data
mapped_data = map_bets(sportybet_response, betpawa_response)

# Pretty print the result
print(json.dumps(mapped_data, indent=4))

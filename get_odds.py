import json
import requests


# Main Paramaters

# API KEYS Will need to be updated regularly
API_KEY = '2c941826a11c8bb41dfc3aa082cdecff'

# SPORT: upcome is any live games and
# the next 8 upcoming games across all sports
SPORT = 'upcoming'

# Region: we've picked the US
REGIONS = 'us'

# Markets: are the type of moneylines
MARKETS = 'h2h,spreads'

# ODDS Format: easier to read than US format
ODDS_FORMAT = 'decimal'

# DATE Format: iso seems standard
DATE_FORMAT = 'iso'

# Default call for in-season sports does NOT
# reduce request quota
sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
    'api_key': API_KEY
})

# check that the request didn't fail
if sports_response.status_code != 200:
    print('Failed to get sports: status_code { sports_response.status_code}, response body {sports_response.text}')
# if it doesn't fail .json() is used to 
#else:
    #print(sports_response.json())

# Making our request for odds
# f-string used for pretty format
odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
    'api_key': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
})

# Check for error code
if odds_response.status_code != 200:
    print('Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
# output
else:
    odds_json = odds_response.json()

    # OUTPUTS TO JSON FILE
    with open("odds_sample.json", "w") as outfile:
        json.dump(odds_json, outfile)
    
    # Check remaining requests
    requests_left = odds_response.headers['x-requests-remaining']
    #print(requests_left)
    requests_used = odds_response.headers['x-requests-used']
    #print(requests_used)
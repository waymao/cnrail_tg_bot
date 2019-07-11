# config.py
# Basic configuration for the app.

# The token of the app
TG_TOKEN = 'TOKEN'

# Time to refresh the train number db, future function, in hrs.
refresh_interval = 24

# WMBot header for better acceptance.
header = {
    'User-Agent': 'Bot/0.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': "1"
}

mysql_info = {
    "host": "host",
    "db": "track",
    "user": "user",
    "password": "password"
}

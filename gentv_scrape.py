import requests
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
import sys

if len(sys.argv) < 2:
    print("Please provide a file name as an argument.")
    sys.exit(1)

file_name = sys.argv[1]

def scrape_views():
    url = 'http://skillhouse.gentv.com'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    script_tag = soup.find('script', id='__NEXT_DATA__')
    json_data = json.loads(script_tag.string)
    return json_data['props']['pageProps']['media']['views']

# Load existing file or create a new one
try:
    results = pd.read_csv(file_name)
except:
    results = pd.DataFrame(columns=['time', 'views'])

scrape_delay = 10
prev_time = time.time()

while True:

    # Get data
    views = scrape_views()
    timestamp = time.time()
    print(f"Scraped at {timestamp}: {views} views")

    # Save data
    results.loc[len(results)] = [timestamp, views]
    results.to_csv(file_name, index=False)

    # Wait for the next time to scrape
    wait_for = scrape_delay - (timestamp - prev_time)
    time.sleep(wait_for)
    prev_time += scrape_delay

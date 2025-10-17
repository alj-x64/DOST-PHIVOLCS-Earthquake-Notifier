import requests
from bs4 import BeautifulSoup
from plyer import notification
import urllib3
import json
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


URL = "https://earthquake.phivolcs.dost.gov.ph/"
STATE_FILE = "C:/Users/aljon/Documents/Python/latest_eq.json"

def get_latest_earthquake():
    response = requests.get(URL, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")

    if len(tables) < 3:
        print("Not enough tables found.")
        return None

    # third table is the table of recent earthquakes
    third_table = tables[2]


    rows = third_table.find_all("tr")
    if len(rows) < 2: #the table that contains the recent earthquakes has 6 columns, the rest tig-iisa or dalawa lang
        print("No data rows found.")
        return None

    # latest earthquake is at the first row, I just treated the header as the ZEROTH row
    first_row = rows[1]
    cols = [c.get_text(strip=True) for c in first_row.find_all("td")]

    # 6 columns yung table kaya pag hindi 6 edi di yun yung table na pagkukuhaan natin
    if len(cols) < 6:
        print("Unexpected table format:", cols)
        return None

    return {
        "datetime": f"{cols[0]}",
        "latitude": cols[1],
        "longitude": cols[2],
        "depth": cols[3],
        "magnitude": cols[4].replace("\u00c2",""), #this should remove the strange symbol before the degree sign.
        "location": cols[5]
    }

def load_last_record():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

def save_last_record(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def notify(eq):
    title = f"Earthquake Alert - Magnitude {eq['magnitude']}"
    message = f"{eq['location']} | {eq['datetime']}"
    print("Notifying:", title, message)
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

def main():
    print("Checking PHIVOLCS earthquake data...")
    while True:
        try:
            
            latest = get_latest_earthquake()
            if not latest:
                print("No earthquake data found.")
                return

            last = load_last_record()
            if not last:
                notify(latest)
                save_last_record(latest)
            elif latest["datetime"] != last["datetime"]:
                notify(latest)
                save_last_record(latest)
            else:
                print("No new earthquake since last check.")
        except requests.exceptions.ConnectionError:
            print("Connection lost.")

    

if __name__ == "__main__":
    main()

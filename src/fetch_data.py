
import requests
from bs4 import BeautifulSoup
import csv

URL = "https://opap.org.cy/en/joker-history"
OUTPUT_FILE = "data/joker_results.csv"

def fetch_joker_results():
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, "html.parser")

    results = []
    rows = soup.select("table tbody tr")

    for row in rows[:78]:  # Παίρνουμε τις 78 πιο πρόσφατες κληρώσεις
        cols = row.find_all("td")
        if len(cols) >= 3:
            date = cols[0].text.strip()
            numbers = cols[1].text.strip().split(" ")
            joker = cols[2].text.strip()
            if len(numbers) == 4:
                results.append([date] + numbers + [joker])

    # Αποθήκευση σε CSV
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Num1", "Num2", "Num3", "Num4", "Joker"])
        writer.writerows(results)

    print(f"✅ Saved {len(results)} results to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_joker_results()

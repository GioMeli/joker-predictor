import requests
from bs4 import BeautifulSoup
import csv
import os

def fetch_latest_results(url="https://opap.org.cy/en/joker-history", max_entries=78):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    results = []
    rows = soup.select("table tbody tr")

    for row in rows[:max_entries]:
        cols = row.find_all("td")
        if len(cols) >= 3:
            date = cols[0].text.strip()
            numbers = cols[1].text.strip().split()
            joker = cols[2].text.strip()
            if len(numbers) == 4:
                results.append([date] + numbers + [joker])
    return results

def save_to_csv(data, filepath="data/joker_results.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Num1", "Num2", "Num3", "Num4", "Joker"])
        writer.writerows(data)

if __name__ == "__main__":
    latest_results = fetch_latest_results()
    save_to_csv(latest_results)
    print(f"✅ Updated 'joker_results.csv' with {len(latest_results)} entries.")

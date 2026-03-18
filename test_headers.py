import requests

url = "https://www.kickstarter.com/discover/advanced?sort=magic&page=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

session = requests.Session()
session.headers.update(headers)

print("Fetching:", url)
try:
    res = session.get(url, timeout=10)
    print("Status:", res.status_code)
    res.raise_for_status()
except Exception as e:
    print("Error:", e)

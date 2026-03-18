import requests
from bs4 import BeautifulSoup
import json

url = "https://www.kickstarter.com/discover/advanced?sort=magic"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

res = requests.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')
if script:
    print("NEXT_DATA exists on discover page")
    data = json.loads(script.string)
    # search for /projects/ strings in the json dump
    s = json.dumps(data)
    import re
    projects = set(re.findall(r'https://www.kickstarter.com/projects/[^/"]+/[^/"]+', s))
    print("Found projects:", len(projects))
    for p in list(projects)[:5]:
        print(p)
else:
    print("No NEXT_DATA on discover either. Saving HTML.")
    with open('discover.html', 'w', encoding='utf-8') as f:
        f.write(res.text)

import requests as r
import bs4 as bs
import re

URL = "https://ycharts.com/indicators/moodys_seasoned_aaa_corporate_bond_yield"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

RESPONSE = r.get(URL, headers=headers)

soup = bs.BeautifulSoup(RESPONSE.text, "html.parser")
bond_value = soup.find("div", class_="key-stat-title").text
bond_value = float(re.search(r"\d+\.\d+", bond_value).group())

print(bond_value)

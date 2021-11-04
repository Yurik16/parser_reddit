import requests
from bs4 import BeautifulSoup

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}


def get_html(url, page=None):
    return requests.get(url, params=page, headers=HEADERS)


def parse():
    html = get_html(URL)
    print(html.status_code)


parse()

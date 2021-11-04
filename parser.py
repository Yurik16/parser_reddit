import requests
from bs4 import BeautifulSoup

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}


def get_html(url, page=None):
    """Getting html from constant with needs HEADERS as request"""
    return requests.get(url, params=page, headers=HEADERS)


def get_content(html):
    """Make a text out of html"""
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.find('div', class_="cZPZhMe-UCZ8htPodMyJ5")
    post = elem.find_all('a')
    print(post)


def parse():
    """Make parsing"""
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print("Please check URL or HEADERS")


parse()

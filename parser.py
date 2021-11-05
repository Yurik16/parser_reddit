import pprint

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}

driver = webdriver.Chrome()


def get_html(url, page=None):
    """Getting html from constant with needs HEADERS as request"""
    return requests.get(url, params=page, headers=HEADERS)


def get_content(html):
    """Make a text out of html"""
    my_lib = []
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.find_all('div', class_="_1RYN-7H8gYctjOQeL8p2Q7")
    for post in elem:
        my_lib.append({
            "username": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE').text[2:],
            "post category": post.find('a', class_='_3ryJoIoycVkA88fy40qNJc', text=True).text[2:],
            "post date": post.find('a', class_='_3jOxDPIQ0KaOWpzvSQo-1s').text,
            "Number of comments": post.find('a', class_='_2qww3J5KKzsD7e5DO0BvvU').text,
            "post karma": post.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text,
        })

    pprint.pprint(my_lib)


def parse():
    """Make parsing"""
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print("Please check URL or HEADERS")


def drv_parse():
    driver.get(url=URL)
    time.sleep(5)
    drv_html = driver.page_source
    get_content(drv_html)


# parse()
drv_parse()

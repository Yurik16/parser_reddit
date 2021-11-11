import pprint
import requests
import time
import uuid

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from collections import defaultdict

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}

driver = webdriver.Chrome()
now_day = datetime.today()
my_lib = defaultdict(list)


def get_html(url, page=None):
    """Getting html from constant with needs HEADERS as request"""
    return requests.get(url, params=page, headers=HEADERS)


def get_content_from_main_page(html):
    """Make a text data out of main html"""
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.find_all('div', class_="_1RYN-7H8gYctjOQeL8p2Q7")
    for post in elem:
        try:
            unique_id = str(uuid.uuid1())
            my_lib[unique_id].append({
                "username": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE').text[2:],
                "post_category": post.find('a', class_='_3ryJoIoycVkA88fy40qNJc', text=True).text[2:],
                "post_date": (now_day - timedelta(
                    int(post.find('a', class_='_3jOxDPIQ0KaOWpzvSQo-1s').text.split(' ')[0]))).strftime('%Y-%m-%d'),
                "Number_of_comments": post.find('a', class_='_2qww3J5KKzsD7e5DO0BvvU').text.split(' ')[0],
                "post_votes": post.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text,
                "user_link": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE')['href'],
                "post_link": post.find('a', class_='SQnoC3ObvgnGjWt90zD9Z')['href']
            })
            parse_user_list(unique_id)
            pprint.pprint(f'{unique_id}->{my_lib[unique_id]}')
        except AttributeError as e:
            print(e)
        except KeyError:
            print("Key error")

    print(len(my_lib))


def parse_user_list(u_id: str) -> None:
    """Make a data dict out of users page"""
    link = my_lib[u_id][0]["user_link"]
    el = f'https://www.reddit.com{link}'
    print(el)
    response = requests.get(el, params=None, headers=HEADERS)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    user_div = soup.find('div', class_='_3Im6OD67aKo33nql4FpSp_')
    try:
        my_lib[u_id][0]["karma"] = user_div.find_next('span', id='profile--id-card--highlight-tooltip--karma').text
        my_lib[u_id][0]["cake_day"] = user_div.find_next('span', id='profile--id-card--highlight-tooltip--cakeday').text
    except AttributeError:
        raise AttributeError("Data error - Users data is restricted")


def get_users_links_list(lib: list) -> list:
    """Make users links list """
    return [f'https://www.reddit.com{elem["user_link"]}' for elem in lib]


def drv_parse() -> None:
    """Make parsing with Chrome"""
    driver.get(url=URL)
    time.sleep(5)
    for _ in range(5):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
        elements = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
        print("Results count: %d" % len(elements))
    drv_html = driver.page_source
    get_content_from_main_page(drv_html)


drv_parse()

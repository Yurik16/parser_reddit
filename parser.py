import pprint
import requests
import time
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}

driver = webdriver.Chrome()
now_day = datetime.today()
my_lib = []


def get_html(url, page=None):
    """Getting html from constant with needs HEADERS as request"""
    return requests.get(url, params=page, headers=HEADERS)


def get_content(html):
    """Make a text data out of main html"""
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.find_all('div', class_="_1RYN-7H8gYctjOQeL8p2Q7")
    for post in elem:
        try:
            my_lib.append({
                "username": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE').text[2:],
                "post category": post.find('a', class_='_3ryJoIoycVkA88fy40qNJc', text=True).text[2:],
                "post date": (now_day - timedelta(
                    int(post.find('a', class_='_3jOxDPIQ0KaOWpzvSQo-1s').text.split(' ')[0]))).strftime('%Y-%m-%d'),
                "Number of comments": post.find('a', class_='_2qww3J5KKzsD7e5DO0BvvU').text.split(' ')[0],
                "post votes": post.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text,
                "user_link": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE')['href']
            })
        except AttributeError:
            print("Data error")

    pprint.pprint(my_lib)
    print(len(my_lib))


def get_users_links_list(lib: list) -> list:
    """Make users links list """
    return [f'https://www.reddit.com{elem["user_link"]}' for elem in lib]


def parse():
    """Make parsing"""
    html = get_html(URL)
    if html.status_code == 200:
        get_content(html.text)
    else:
        print("Please check URL or HEADERS")


def drv_parse():
    """Make parsing with Chrome"""
    driver.get(url=URL)
    time.sleep(5)
    for _ in range(2):
        elements = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
        print("Results count: %d" % len(elements))
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
    drv_html = driver.page_source
    get_content(drv_html)
    ull = get_users_links_list(my_lib)
    pprint.pprint(ull)


def parse_user_list(lib: list):
    """Make a data dict out of users page"""
    users_page = {}
    for el in lib:
        response = requests.get(el)
        if response.status_code == 200:
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            user_div = soup.find('div', class_='_3Im6OD67aKo33nql4FpSp_')
            try:
                users_page[f'{el[28:-1]} user'] = user_div.find('span', class_='_28nEhn86_R1ENZ59eAru8S').text.split(' ')[0][2::]
                users_page[f'{el[28:-1]} karma'] = user_div.find('span', id='profile--id-card--highlight-tooltip--karma').text
                # user_page["cake day"] = user_div.find_next('span', class_='_3KNaG9-PoXf4gcuy5_RCVy').text
            except AttributeError:
                print("Data error")
        else:
            print("Please check URL or HEADERS")
    pprint.pprint(users_page)


drv_parse()
ull = get_users_links_list(my_lib)
parse_user_list(ull)

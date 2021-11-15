import json
from datetime import datetime, timedelta
import pprint
import requests
import time
import uuid

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

# dict with result data from web
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
            get_users_data_from_json(unique_id)
        except AttributeError as e:
            print(e or "Data error - Post data incorrect")
            del my_lib[unique_id]
        # pprint.pprint(f'{unique_id}->{my_lib[unique_id]}')

    print(len(my_lib))


def parse_user_data(u_id: str) -> None:
    """
    Make a data dict out of users page
    :param u_id: Unique id made by uuid
    :return: None
    """
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


def get_users_data_from_json(u_id: str):
    """
    Getting users data from json response by making myself request
    :param u_id: uuid
    """
    name = my_lib[u_id][0]["username"]
    url = f'https://www.reddit.com/user/{name}/about.json?'
    r = requests.get(url, params=None, headers=HEADERS)
    user_json = r.json()
    try:
        my_lib[u_id][0]["total_karma"] = user_json["data"]["total_karma"]
        my_lib[u_id][0]["comment_karma"] = user_json["data"]["comment_karma"]
        my_lib[u_id][0]["link_karma"] = user_json["data"]["link_karma"]
        my_lib[u_id][0]["cake_day"] = datetime.fromtimestamp(user_json["data"]["created"]).strftime('%Y/%m/%d %H:%M')
    except AttributeError:
        raise AttributeError("Data error - Users data is restricted")


def get_users_links_list(lib: list) -> list:
    """
    Make users links list
    :param lib: list of dicts with post data
    :return: list of links on users page
    """
    return [f'https://www.reddit.com{elem["user_link"]}' for elem in lib]


def drv_parse() -> None:
    """Make parsing with Chrome"""
    driver.get(url=URL)
    time.sleep(5)
    elem_counter = 0
    while elem_counter < 40:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(2)
        elements = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
        elem_counter = len(elements)
        print("Results count: %d" % elem_counter)
    drv_html = driver.page_source
    get_content_from_main_page(drv_html)


def get_txt_file(l: dict) -> None:
    """
    Convert result dict to txt
    :param l: result dict with parsing data
    :return: None
    """
    time_str = str(datetime.now().strftime("%Y%m%D%H%M").replace("/", ""))
    with open(f'reddit-{time_str}.txt', 'w') as file:
        file.write(json.dumps(l))


drv_parse()
get_txt_file(my_lib)

import pprint
import requests
import time
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

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


def get_content_from_main_page(html):
    """Make a text data out of main html"""
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.find_all('div', class_="_1RYN-7H8gYctjOQeL8p2Q7")
    for post in elem:
        try:
            my_lib.append({
                "username": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE').text[2:],
                "post_category": post.find('a', class_='_3ryJoIoycVkA88fy40qNJc', text=True).text[2:],
                "post_date": (now_day - timedelta(
                    int(post.find('a', class_='_3jOxDPIQ0KaOWpzvSQo-1s').text.split(' ')[0]))).strftime('%Y-%m-%d'),
                "Number_of_comments": post.find('a', class_='_2qww3J5KKzsD7e5DO0BvvU').text.split(' ')[0],
                "post_votes": post.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text,
                "user_link": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE')['href'],
                "post_link": post.find('a', class_='SQnoC3ObvgnGjWt90zD9Z')['href']
            })
        except AttributeError:
            print("Data error")
        except KeyError:
            print("Key error")

    pprint.pprint(my_lib)
    print(len(my_lib))


def get_users_name(lib: list) -> list:
    """Make users links list """
    return [elem["user_link"][6:-2] for elem in lib]


def get_users_links_list(lib: list) -> list:
    """Make users links list """
    return [f'https://www.reddit.com{elem["user_link"]}' for elem in lib]


def parse():
    """Make parsing"""
    html = get_html(URL)
    if html.status_code == 200:
        get_content_from_main_page(html.text)
    else:
        print("Please check URL or HEADERS")


def drv_parse() -> None:
    """Make parsing with Chrome"""
    driver.get(url=URL)
    time.sleep(5)
    for _ in range(2):
        elements = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
        print("Results count: %d" % len(elements))
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(3)
    drv_html = driver.page_source
    get_content_from_main_page(drv_html)
    # ull = get_users_links_list(my_lib)
    # pprint.pprint(ull)


def parse_user_list(lib: list) -> None:
    """Make a data dict out of users page"""
    users_page = []
    for el in lib:
        print(el)
        response = requests.get(el, params=None, headers=HEADERS)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        user_div = soup.find('div', class_='_3Im6OD67aKo33nql4FpSp_')
        try:
            users_page.append({
                "username": f'{el[28:-1]}',
                # "user": user_div.find('span', class_='_28nEhn86_R1ENZ59eAru8S').text,
                "karma": user_div.find_next('span', id='profile--id-card--highlight-tooltip--karma').text,
                "cake day": user_div.find_next('span', id='profile--id-card--highlight-tooltip--cakeday').text,
            })
        except AttributeError:
            print("Data error")

    def parse_user_data_to_add_my_lib(l: list) -> None:
        """Add data to my_lib"""
        for user_link in l:
            print(user_link)
            response = requests.get(user_link, params=None, headers=HEADERS)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            user_div = soup.find('div', class_='_3Im6OD67aKo33nql4FpSp_')
            for user_data in my_lib:
                u_name = user_data["username"]
                div_u_name = user_div.find('span', class_='_28nEhn86_R1ENZ59eAru8S').text
                if user_data[u_name] == div_u_name:
                    try:
                        user_data.append({
                            # "username": f'{user_link[28:-1]}',
                            # "user": user_div.find('span', class_='_28nEhn86_R1ENZ59eAru8S').text,
                            "karma": user_div.find_next('span', id='profile--id-card--highlight-tooltip--karma').text,
                            "cake day": user_div.find_next('span',
                                                           id='profile--id-card--highlight-tooltip--cakeday').text,
                        })
                    except AttributeError:
                        print("Data error")

    pprint.pprint(users_page)
    print(len(users_page))


def get_users_data_from_json(lib: list) -> list:
    """
    Getting users data from json response by making myself request
    :param lib: list wuth names of users
    :return: list of dict with users detail
    """
    users_data = []
    for name in lib:
        url = f'https://www.reddit.com/user/{name}/about.json?redditWebClient=web2x&app=web2x-client-production&gilding_detail=1&awarded_detail=1&raw_json=1'
        r = requests.get(url, params=None, headers=HEADERS)
        user_json = r.json()
        with open(f'user_{name}.json', 'wb') as u_json:
            u_json.write(r.content)
        try:
            users_data.append({
                "name": user_json["data"]["name"],
                "total_karma": user_json["data"]["total_karma"],
                "comment_karma": user_json["data"]["comment_karma"],
                "cake_day": datetime.fromtimestamp(user_json["data"]["created"])
            })
        except AttributeError:
            print("Data error")
        pprint.pprint(type(user_json))
        pprint.pprint(user_json)
    return users_data


drv_parse()
ull = get_users_links_list(my_lib)
parse_user_list(ull)


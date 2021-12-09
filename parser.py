import argparse
import json
import logging
import time
import uuid
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': f'Mozilla/5.0 (Windows NT 10.0;' +
                  f' Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}
STORE_DATA_AS_DICT = {}  # dict with result data from web
ARGS = object  # argparse obj, gets attributes: count (numbers of parsing posts) and filepath (result_txt file path)


def logging_init() -> None:
    """Init logging"""
    logging.basicConfig(filename="log.txt", filemode='a',
                        format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s',
                        level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


def driver_init() -> "driver":
    """Init WebDriver
    :return: web browser driver
    """
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=options)
    return driver


def argparse_init(num_of_posts=10, filepath="") -> "args":
    """Init argparse module
    :param num_of_posts:
    :param filepath:
    :return: argparse module object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", metavar="count", type=int, default=num_of_posts, help="number of parsing posts")
    parser.add_argument("--filepath", metavar="filepath", type=str, default=filepath, help="filepath to result txt")
    args = parser.parse_args()
    return args


def get_html(url, page=None):
    """Getting html from constant with needs HEADERS as request"""
    return requests.get(url, params=page, headers=HEADERS)


def get_content_from_main_page(html):
    """Make a text data out of main html"""
    logging.info("Start parsing data")
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.find_all('div', class_="_1RYN-7H8gYctjOQeL8p2Q7")
    for post in elem:
        try:
            unique_id = str(uuid.uuid1())
            STORE_DATA_AS_DICT[unique_id] = []  # can use defaultDict(list)
            STORE_DATA_AS_DICT[unique_id].append({
                "username": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE').text[2:],
                "post_category": post.find('a', class_='_3ryJoIoycVkA88fy40qNJc', text=True).text[2:],
                "post_date": (datetime.today() - timedelta(
                    int(post.find('a', class_='_3jOxDPIQ0KaOWpzvSQo-1s').text.split(' ')[0]))).strftime('%Y/%m/%d'),
                "Number_of_comments": post.find('a', class_='_2qww3J5KKzsD7e5DO0BvvU').text.split(' ')[0],
                "post_votes": post.find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text,
                "user_link": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE')['href'],
                "post_link": post.find('a', class_='SQnoC3ObvgnGjWt90zD9Z')['href']
            })
            get_users_data_from_json(unique_id)
        except AttributeError as e:
            # Catch errors (if Live Stream or 18+) and exclude that unit from result data
            logging.warning(e or "Data error - Post data incorrect")
            del STORE_DATA_AS_DICT[unique_id]
        except KeyError as k_e:
            logging.warning(k_e)
            del STORE_DATA_AS_DICT[unique_id]
        try:
            payload = json.dumps(
                {"data": {unique_id: STORE_DATA_AS_DICT[unique_id][0]}, "metadata": {"filepath": ARGS.filepath}})
            requests.post('http://localhost:8000/posts/', data=payload)
        except ConnectionError as ce:
            logging.warning(ce)
        if len(STORE_DATA_AS_DICT.keys()) >= ARGS.count:
            logging.info("Parsing data Done")
            break


def get_users_data_from_json(u_id: str):
    """Getting users data from json response by making myself request
    :param u_id: uuid
    """
    name = STORE_DATA_AS_DICT[u_id][0]["username"]
    url = f'https://www.reddit.com/user/{name}/about.json?'
    r = requests.get(url, params=None, headers=HEADERS)
    user_json = r.json()
    try:
        STORE_DATA_AS_DICT[u_id][0]["total_karma"] = user_json["data"]["total_karma"]
        STORE_DATA_AS_DICT[u_id][0]["comment_karma"] = user_json["data"]["comment_karma"]
        STORE_DATA_AS_DICT[u_id][0]["link_karma"] = user_json["data"]["link_karma"]
        STORE_DATA_AS_DICT[u_id][0]["cake_day"] = datetime.fromtimestamp(user_json["data"]["created"]).strftime(
            '%Y/%m/%d %H:%M')
    except AttributeError:
        # Catch errors (content 18+) and throw it to next except
        raise AttributeError("Data error - Users data is restricted")
    except KeyError:
        # Catch errors (user deleted) and throw it to next except
        raise AttributeError("Data error - Users data is restricted")


def pause_till_browser_load(browser, timeout=5) -> None:
    """Waiting while browser loads the elements
    :param browser: browser driver
    :param timeout: time in sec
    :return: None
    """
    try:
        myElem = WebDriverWait(browser, timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')))
    except TimeoutError:
        logging.warning("Timed out waiting for page to load")


def drv_parse() -> None:
    """Make parsing with Chrome"""
    logging.info("Start scrolling page")
    driver = driver_init()
    driver.get(url=URL)
    time.sleep(3)
    elem_counter = 0
    while elem_counter < ARGS.count + 10:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        pause_till_browser_load(driver)
        elements = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
        elem_counter = len(elements)
    logging.info("Scrolling page Done")
    drv_html = driver.page_source
    get_content_from_main_page(drv_html)


def get_list_from_dict(data: dict) -> list:
    """Convert result dict to list
    :param data: result dict with parsing data
    :return: None
    """
    # logging.info("Convert data to list")
    result_list = []
    for key, val in data.items():
        if len(result_list) < ARGS.count:
            result_list.append(f'{key};' +
                               f' https://www.reddit.com/{val[0]["post_link"]};' +
                               f' {val[0]["username"]};' +
                               f' {val[0]["total_karma"]};' +
                               f' {val[0]["cake_day"]};' +
                               f' {val[0]["link_karma"]};' +
                               f' {val[0]["comment_karma"]};' +
                               f' {val[0]["post_date"]};' +
                               f' {val[0]["Number_of_comments"]};' +
                               f' {val[0]["post_votes"]};' +
                               f' {val[0]["post_category"]}'
                               )
    return result_list


def file_create():
    logging.info("Convert list to txt")
    time_str = str(datetime.now().strftime("%Y%m%D%H%M").replace("/", ""))
    with open(f'{ARGS.filepath}reddit-{time_str}.txt', 'w', encoding="utf-8") as file:
        file.write("\n".join(get_list_from_dict(STORE_DATA_AS_DICT)))


if __name__ == '__main__':
    logging_init()
    ARGS = argparse_init()
    logging.info("Start Program !!!")
    drv_parse()
    # get_list_from_dict(STORE_DATA_AS_DICT)
    logging.info("End program \n")

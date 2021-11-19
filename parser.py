import requests
import time
import uuid
import logging
import argparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from collections import defaultdict
from datetime import datetime, timedelta

URL = 'https://www.reddit.com/top/?t=month'
HEADERS = {
    'user-agent': f'Mozilla/5.0 (Windows NT 10.0;' +
                  f' Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*'
}
logging.basicConfig(filename="log.txt", filemode='a',
                    format='%(asctime)s :: %(levelname)s :: %(funcName)s :: %(lineno)d :: %(message)s',
                    level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)

now_day = datetime.today()
parser = argparse.ArgumentParser()
parser.add_argument("--count", metavar="count", type=int, default=100, help="num_of_parsing_posts")
parser.add_argument("--filepath", metavar="filepath", type=str, default="", help="filepath to result txt")
args = parser.parse_args()

# dict with result data from web
my_lib = defaultdict(list)
# number of parsing posts
num_of_parsing_posts = args.count


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
            my_lib[unique_id].append({
                "username": post.find('a', class_='oQctV4n0yUb0uiHDdGnmE').text[2:],
                "post_category": post.find('a', class_='_3ryJoIoycVkA88fy40qNJc', text=True).text[2:],
                "post_date": (now_day - timedelta(
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
            del my_lib[unique_id]
        except KeyError as k_e:
            logging.warning(k_e)
            del my_lib[unique_id]
        # print(round(float(len(my_lib) / (num_of_parsing_posts + 20) * 100), 2), "%")
    logging.info("Parsing data Done")


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
        # Catch errors (content 18+) and throw it to next except
        raise AttributeError("Data error - Users data is restricted")
    except KeyError:
        # Catch errors (user deleted) and throw it to next except
        raise AttributeError("Data error - Users data is restricted")


def get_users_links_list(lib: list) -> list:
    """
    Make users links list
    :param lib: list of dicts with post data
    :return: list of links on users page
    """
    return [f'https://www.reddit.com{elem["user_link"]}' for elem in lib]


def pause_till_browser_load(browser, timeout: int) -> None:
    try:
        myElem = WebDriverWait(browser, timeout).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')))
    except TimeoutError:
        logging.warning("Timed out waiting for page to load")


def drv_parse() -> None:
    """Make parsing with Chrome"""
    logging.info("Start scrolling page")
    driver.get(url=URL)
    time.sleep(3)
    elem_counter = 0
    while elem_counter < num_of_parsing_posts + 20:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        pause_till_browser_load(driver, 5)
        # time.sleep(2)
        elements = driver.find_elements(By.CLASS_NAME, '_1oQyIsiPHYt6nx7VOmd1sz')
        elem_counter = len(elements)
        # print("Results count: %d" % elem_counter)
    logging.info("Scrolling page Done")
    drv_html = driver.page_source
    get_content_from_main_page(drv_html)


def get_txt_file(data: dict) -> None:
    """
    Convert result dict to txt
    :param data: result dict with parsing data
    :return: None
    """
    logging.info("Convert data to txt")
    time_str = str(datetime.now().strftime("%Y%m%D%H%M").replace("/", ""))
    result_list = []
    for key, val in data.items():
        if len(result_list) < num_of_parsing_posts:
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
    with open(f'{args.filepath}reddit-{time_str}.txt', 'w', encoding="utf-8") as file:
        file.write("\n".join(result_list))


if __name__ == '__main__':
    logging.info("Start Program !!!")
    drv_parse()
    get_txt_file(my_lib)
    logging.info("End program \n")

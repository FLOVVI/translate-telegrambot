from config import request_login, request_password

from bs4 import BeautifulSoup as bs
import requests
from googletrans import Translator

session = requests.Session()

URL = "https://www.pythonanywhere.com/login/"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0",
    "Referer": "https://www.pythonanywhere.com/login/"
}


def get_token():
    response_get = session.get(URL, headers=headers)
    token_soup = bs(response_get.text, "lxml")
    token = token_soup.find('input', type='hidden')['value']
    return token


data = {
    "csrfmiddlewaretoken": get_token(),
    "auth-username": request_login,
    "auth-password": request_password,
    "login_view-current_step": "auth"
}


def server_load():
    # Get a token
    data['csrfmiddlewaretoken'] = get_token()
    print(data)
    # We receive data after registration
    response = session.post(URL, data=data, headers=headers)
    soup = bs(response.text, "lxml")
    # Data
    usage_percentage = soup.find('span', id='id_daily_cpu_usage_percent').text
    usage_second = soup.find('span', id='id_daily_cpu_usage_percent').text
    usage_max_second = soup.find('span', id='id_daily_cpu_usage_allowance').text
    resets_text = soup.find('span', id="id_daily_cpu_reset_time").text
    return ServerLoad(usage_percentage, usage_second, usage_max_second, resets_text)


class ServerLoad:
    def __init__(self, usage_percentage, usage_second, usage_max_second, resets_text):
        self.usage_percentage = usage_percentage
        self.usage_second = usage_second
        self.usage_max_second = usage_max_second
        self.resets_text = resets_text
        self.statistics_text = f"CPU использовано: {self.usage_percentage}% - {self.usage_second}/{self.usage_max_second} секунд. Сброс через {Translator().translate(self.resets_text, dest='ru').text}"
import re
import requests
from bs4 import BeautifulSoup
import asyncio
from typing import Tuple

def get_city_code() -> dict:
    city_code = ""
    with open("city_code.txt", "r") as file:
        city_code = file.read()
    pattern = re.compile(r'{ name : (.*?) , id : (\d+?) }')
    city_code_list = pattern.findall(city_code)
    city_code_dict = {}
    for item in city_code_list:
        # 有英文的情况， 类似  纽约(NewYork)
        if (item[0].find('(') != -1):
            tempStr = item[0][:item[0].find('(')]
        else :
            tempStr = item[0]
        city_code_dict[tempStr] = item[1]
    return city_code_dict

async def get_weather(city : str, city_code : str) -> list:
    url = "http://www.weather.com.cn/weather/"+city_code+".shtml"
    headers = {
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    r = requests.get(url, headers = headers)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, features="html.parser")
    SevenDayData = soup.find("div", class_ = 'c7d')
    # find 返回的结果可继续find
    # find_all 返回的是 ResultSet, 也即 List
    ul = SevenDayData.find("ul")
    li = ul.find_all("li")
    weather = {}
    for day in li:
        wea_list = []
        date = day.find("h1").string      # 日期
        # 总体天气情况
        wea_1 = day.find("p", class_ = "wea")
        wea_list.append(wea_1.string)
        # 气温范围
        wea_2 = day.find("p", class_ = "tem")
        least_tem = wea_2.find("i").string
        if wea_2.find("span") is None:
            tem_range = least_tem
        else :
            highest_tem = wea_2.find("span").string
            tem_range = least_tem + " ~ " + highest_tem
        wea_list.append(tem_range)
        # 风向与风速
        wea_3 = day.find("p", class_ = "win")
        win = wea_3.find("span")["title"]
        win_level = wea_3.find("i").string
        wea_list.append(win + " " + win_level)

        weather[date] = wea_list        
    return (url, weather)

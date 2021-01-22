# -*- coding:utf-8 -*-

# @Time    : 2021/1/20
# @Author  : Crepuscule-v
# @FileName: getSinaweibo.py

from fake_useragent import UserAgent
import requests
import time
import re
import json  
import asyncio 
import sys
from bs4 import BeautifulSoup
from typing import List, Dict, Set
blog_id_set = set()

# request.session 用于实现客户端和服务端的会话保持
user_agent = UserAgent()
sleep_time = 1
headers = {
    "User-Agent" : user_agent.random
}
def timeTrans(
    time_string : str, 
    from_format = '%a %b %d %H:%M:%S %z %Y', 
    to_format = '%Y-%m-%d %H:%M:%S',
):
    tempTime = time.strptime(time_string, from_format)
    ansTime = time.strftime(to_format, tempTime)
    return ansTime

async def get_basic_info(name : str) -> Dict:
    url = f'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{name}&page_type=searchall'
    headers["User-Agent"] = user_agent.random
    r = requests.get(url, headers = headers, timeout = 1)
    r.encoding = 'utf-8'
    raw = json.loads(r.text)
    cards_1 = raw["data"]["cards"][0]
    card_group_1 = cards_1["card_group"][0]
    user = card_group_1["user"]
    personalInfo_dict = {
        'uid' : user["id"],
        "nickname" : user["screen_name"],
        "profile_img" : user["profile_image_url"],
        "profile_url" : user["profile_url"],
        "followers_count" : user["followers_count"], # 粉丝数量
        # "follow_count" : user["follow_count"],
        "description" : user["description"],
    }
    personalInfo_dict["verified_reason"] = ""
    if "verified_reason" in user:
        personalInfo_dict["verified_reason"] = user["verified_reason"] # 认证标签
    return personalInfo_dict

# 对于每一篇blog先找blog的id, 然后 去"https://m.weibo.cn/status/{id}" 找对应的lobg
async def get_blog_from_id(blog_id : str) -> Dict:
    blog_url = f"https://m.weibo.cn/status/{blog_id}"
    headers["User-Agent"] = user_agent.random
    blog_r = requests.get(blog_url, headers, timeout = 2)
    blog_r.encoding = 'utf-8'
    raw_status = re.search(r'\[{(.*})?\]',blog_r.text, re.DOTALL)
    if raw_status is not None:
        raw_status = raw_status.group(1)
        raw_str = re.search(r'^(.*)?"hotScheme"(.*)?$', raw_status, re.DOTALL)
        # 最后还多一个逗号
        if raw_str is not None:
            raw_str = raw_str.group(1)
            raw_str = re.search(r'^.*?{(.*)?,\s*$', raw_str, re.DOTALL)
            if raw_str is not None:
                raw_str = '{' + raw_str.group(1)
            else:
                raw_str = None
        else:
            raw_str = None
    else:
        raw_str = None
    if raw_str == None:
        return {}
    status = json.loads(raw_str)
    blog_text = status["text"]
    blog_text = re.sub(r'<br />', '\n', blog_text, re.DOTALL)
    blog_text = re.sub(r'<.*?>', '', blog_text, re.DOTALL)
    blog_text = re.sub(r'\[ *', '[', blog_text, re.DOTALL)
    blog_text = re.sub(r'\【 *', '【', blog_text, re.DOTALL)
    blog_text = re.sub(r' *]', ']\n', blog_text, re.DOTALL)
    blog_text = re.sub(r' *】', '】\n', blog_text, re.DOTALL)
    blog_text = re.sub(r';|；', ';\n', blog_text, re.DOTALL)
    blog_text = re.sub(r'<.*?>', ' ', blog_text, re.DOTALL)
    # 发博时间为中国标准时间, 需要转化
    raw_blog_time = status["created_at"]  
    blog_time = timeTrans(raw_blog_time)
    blog_imgs = []
    if "pics" in status:
        raw_blog_imgs = status["pics"]
        if raw_blog_imgs.__len__() != 0:
            for image in raw_blog_imgs:
                blog_imgs.append(image["large"]["url"])
    single_blog_info = {
        "blog_id" : blog_id,
        "blog_time" : blog_time,
        "blog_text" : blog_text,
        "attitudes_count" : status["attitudes_count"],
        "reposts_count" : status["reposts_count"],
        "comments_count" : status["comments_count"],
        "blog_imgs" : blog_imgs,
        "source" : status["source"]     # phone
    }
    return single_blog_info

async def get_blog(name : str, num : int = 2) -> List:
    info_dict = await get_basic_info(name)
    if num == 0:
        return [info_dict]
    blog_info_list = []
    url = "https://m.weibo.cn/profile/info?uid={}".format(info_dict["uid"])
    headers["User-Agent"] = user_agent.random
    r = requests.get(url, headers = headers, timeout = 3)
    r.encoding = 'utf-8'
    raw_blogs = json.loads(r.text)["data"]["statuses"]
    for blog in raw_blogs:
        blog_id = blog["id"]
        blog_id_set.add(blog_id)
        single_blog_info = await get_blog_from_id(blog_id)
        if single_blog_info is not {}:
            blog_info_list.append(single_blog_info)
        await asyncio.sleep(sleep_time)
        if blog_info_list.__len__() >= num:
            break
    # with open("test.json", 'a', encoding='utf-8') as file:
    #     for item in blog_info_list:
    #         file.write(str(item))
    #         file.write('\n')
    return blog_info_list

#DEBUG
if __name__ == '__main__':
    pass
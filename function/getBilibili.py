# -*- coding:utf-8 -*-

# @author: Crepuscule_v
# @time  : 2020/1/22 
# @file  : Bilibili.py
'''
1. 给出B站视频的BV号, 下载该视频, 可选集
2. 给定某一Up主，下载其全部视频
'''
from typing import List
from bs4 import BeautifulSoup
from function.config import Dir as Dir
import requests
import json
import os
import math
import asyncio
import re

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
}
headers_1 = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9",
    # "access-control-request-headers": "range",
    "access-control-request-method": "GET",
    "cache-control": "no-cache",
    "origin": "https://www.bilibili.com",
    "pragma": "no-cache",
    "referer": "https://www.bilibili.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
}
headers_2 = {
    "accept": "*/*",
    "accept-encoding": "identity",
    "accept-language": "zh-CN,zh;q=0.9",
    "cache-control": "no-cache",
    "dnt": "1",
    "origin": "https://www.bilibili.com",
    "pragma": "no-cache",
    "referer": "https://www.bilibili.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
}

async def GetBilibiliVideo(parm : List, raw_path : str) -> bool:
    try:
        BV_id, p, video_info = parm[0], parm[1], parm[2]
        dash = json.loads(video_info)["data"]["dash"]
        video = dash["video"]
        video_url = video[0]["baseUrl"]
        audio_url = dash["audio"][0]["baseUrl"]
        sess = requests.session()
        sess.options(video_url, headers = headers_1)
        r_1 = sess.get(video_url, headers = headers_2)
        r_2 = sess.get(audio_url, headers = headers_2)
        with open(f"{raw_path}\\{BV_id}_p{p}_video.mkv", "wb") as file:
            file.write(r_1.content)
            file.close()
        with open(f"{raw_path}\\{BV_id}_p{p}_audio.mkv", "wb") as file:
            file.write(r_2.content)
            file.close()
        await CombinevideoAudio(
            f"{raw_path}\\{BV_id}_p{p}_video.mkv", 
            f"{raw_path}\\{BV_id}_p{p}_audio.mkv", 
            f"{raw_path}\\p{p}.mkv"
        )
        return True
    except:
        return False
async def CombinevideoAudio(videopath, audiopath, outpath):
    os.system("D:\\Python\\ffmpeg-4.3.1-2021-01-01-full_build\\bin\\ffmpeg.exe -i " + audiopath + ' -i ' + videopath + " " + outpath)
    if os.path.exists(videopath):
        os.remove(videopath)
    if os.path.exists(audiopath):
        os.remove(audiopath)
async def GetVideoInfo(BV_id : str, p : int) -> List:
    url = f"https://www.bilibili.com/video/{BV_id}/?p={p}"
    # try:
    r = requests.get(url, headers)
    r.encoding = 'utf-8'
    video_info = re.search(r'<script>window.__playinfo__=(.*?)</script>', r.text, re.DOTALL).group(1)
    brief_introduction = re.search(r'<script>window.__INITIAL_STATE__=(.*?);\(function\(\)', r.text, re.DOTALL)
    brief_introduction_json = json.loads(brief_introduction.group(1))
    videoData = brief_introduction_json["videoData"]
    # with open("test.json", "w", encoding="utf-8") as file:
    #     file.write(str(videoData))

    # Attention : encode 将 str 变为 raw bytes, decode 将 raw bytes 变为 str
    # 此视频的一些基本信息, 按需再做处理
    basic_info = {
        "bvid"      : videoData["bvid"],                                                # BV号
        "title"     : videoData["title"],                                               # 标题
        "desc"      : videoData["desc"],                                                # 视频描述
        "video_num" : videoData["videos"],                                              # 视频集数
        "pic_url"   : videoData["pic"].encode().decode("unicode-escape"),               # 封面链接
        "up_name"   : videoData["owner"]["name"],                                       # Up主昵称
        "reply"     : videoData["stat"]["reply"],                                       # 回复数
        "coin"      : videoData["stat"]["coin"],                                        # 投币数
        "like"      : videoData["stat"]["like"],                                        # 喜欢
        "dislike"   : videoData["stat"]["dislike"],                                     # 不喜欢
        "share"     : videoData["stat"]["share"],                                       # 分享
        "favorite"  : videoData["stat"]["favorite"]                                     # 收藏
    }
    return [basic_info, video_info]
async def DownloadBilibili(BV_id : str, p_start : int = 0, p_end : int = 0, general_path : str = Dir) -> bool:
    '''
    指定BV号下载视频
    多P情况下可指定下载 [p_start - p_end], 不指定则默认全部下载
    单P情况下可忽略后两个参数
    '''
    if p_start > p_end:
        p_start, p_end = p_end, p_start                                                     # 解决眼睛不好使的用户的问题
    video_info_list = await GetVideoInfo(BV_id, 1)                                          # 先获得这个视频的整体信息
    p_num = video_info_list[0]["video_num"]
    up_name = video_info_list[0]["up_name"]
    title = video_info_list[0]["title"]
    title = re.sub(r'[^\u4e00-\u9fa5]', "_", title)                                         # 去掉 title 中所有非汉字字符, 以防路径命名错误
    raw_path = general_path +  f"\\{up_name}_{BV_id}_{title}"
    if os.path.exists(raw_path):                                                            # 创建新文件夹来保存视频
        print("该文件夹已存在, 请您重新确认视频保存路径是否正确")
        return False
    else:
        os.system(f"mkdir {raw_path}")                                                        
    if p_start < 0 or p_end > p_num:
        print("您输入的视频集数超出集数范围, 默认下载全部")
        p_start = 0
        p_end = 0
    if (p_start == 0 and p_end == 0) or p_num == 1:                                         # 全部下载
        print(f"正在下载{BV_id}...")
        video_info_list = await GetVideoInfo(BV_id, 1)                    
        video_info = video_info_list[1]
        flag = await GetBilibiliVideo([BV_id, 1, video_info], raw_path)
        if flag:
            print("{BV_id} : 下载成功")
        else:
            print("{BV_id} : 下载失败")
    else:  
        flag = True                                                                                 # 部分下载
        for i in range(p_start, p_end + 1):
            print(f"正在下载p{i}...")
            video_info_list = await GetVideoInfo(BV_id, i)                    
            video_info = video_info_list[1]
            temp_flag = await GetBilibiliVideo([BV_id, i, video_info], raw_path)
            if temp_flag:
                print(f"{BV_id}___p{i} : 下载完成")
            else:
                flag = False
                print(f"{BV_id}___p{i} : 下载失败")
        if flag:
            print(f"{BV_id} : 下载成功")
        else:
            print(f"{BV_id} : 部分选集下载失败")
    return True
async def GetUpMid(Up_name : str) -> int:
    '''
    下载某个Up主的所有作品
    '''
    url = f"https://search.bilibili.com/all?keyword={Up_name}"
    r = requests.get(url, headers)
    r.encoding = 'utf-8'
    # with open("test.html", "w", encoding='utf-8') as file:
    #     file.write(r.text)
    soup = BeautifulSoup(r.content, "html.parser")
    info = soup.find("div", class_ = "up-face")
    Up_mid = re.search(r'com/(.*?)\?from',info.a["href"]).group(1)
    return Up_mid
async def GetPageNum(Up_mid : int) -> int:
    video_list_url = f"https://api.bilibili.com/x/space/arc/search?mid={Up_mid}"
    r = requests.get(video_list_url, headers)
    r.encoding = 'utf-8'
    # with open('test.json', 'w', encoding='utf-8') as file:
    #     file.write(r.text)
    data = json.loads(r.text)["data"]
    VideoNum = data["page"]["count"]    # 该 Up主总视频数
    VideoPerPage = data["page"]["ps"]
    Pages = math.ceil(VideoNum / VideoPerPage)   # 总页数
    return Pages
async def GetAllVideo(Pages : int, Up_mid : int, general_path : str):
    cnt = 1                                                             
    for i in range(1, Pages + 1):
        video_list_url = f"https://api.bilibili.com/x/space/arc/search?mid={Up_mid}&pn={i}"
        r = requests.get(video_list_url, headers)
        r.encoding = 'utf-8'
        with open('test.json', 'a', encoding='utf-8') as file:
            file.write(r.text)
        data = json.loads(r.text)["data"]
        vlist = data["list"]["vlist"]
        for video in vlist:
            bvid = video["bvid"]
            flag = await DownloadBilibili(bvid, 0, 0, general_path)
            if flag:
                print(f"第 [{i}] 页, Video [{cnt}]下载成功")
                cnt += 1
            else:
                print(f"第 [{i}] 页, Video [{cnt}]下载失败")
        print(f"Page [{i}] 全部下载完毕")
async def GetVideoByUp(Up_name : str) -> bool:
    Up_mid = await GetUpMid(Up_name)
    Page_num = await GetPageNum(Up_mid)
    general_path = f"{Dir}\\{Up_name}"
    if os.path.exists(general_path):
        print("该文件夹已存在, 请您重新确认视频保存路径是否正确") 
    else:
        os.system(f"mkdir {general_path}")
    await GetAllVideo(Page_num, Up_mid, general_path)

# DEBUG
if __name__ == "__main__":
    # 可指定自己的视频保存目录 -> Dir
    # 遇到通过检测 ip反爬虫时, 可以尝试使用 fake_useragent 伪装 User-Agent
    # 默认下载视频为最高清晰度
    asyncio.run(GetVideoByUp("黄霄云"))                      # 通过 Up主名字下载视频
    asyncio.run(DownloadBilibili("BV1Rz4y1U7ZH", 0, 0))     # 通过 BV 号下载视频, 参数[2, 3]表示某一视频有多集情况下可指定下载范围，默认全部下载